import subprocess
import os
import threading
from time import sleep

from common.module.module import Module
from common.gpb.python.SSD_pb2 import SSDRequest, SSDResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.modules.ssd.ssd_Exception import SSDModuleException

## Discard the output
DEVNULL = open(os.devnull, 'wb')

## Collects IO information
#
class collectIO(threading.Thread):
    ## Constructor
    #  @param   self
    #  @param   sleeptime   Number of seconds to sleep DEFAULT = [1]
    def __init__(self, device, sleeptime=1):
        # Initializes threading
        threading.Thread.__init__(self)
        ## Lock for preventing thread issues
        self.lock = threading.Lock()
        ## Device name
        self.device = device
        ## Sleeptime in seconds
        self.sleeptime = sleeptime
        ## Write count in Megabytes
        self.write = 0.0
        ## Read count in Megabytes
        self.read = 0.0
        ## Thread exits when self.quit = True
        self.quit = False

    ## Grabs IO statistics from Linux
    #  Retreives IO information from '/proc/diskstats' and parses necessary information
    #  @param   self
    #  @return  io_infos   Array containing data read from diskstats
    def getioData(self):
        with open('/proc/diskstats', 'r') as io_stats:
            #  Parses Linux IO data from diskstats file
            for content in io_stats.readlines():
                for line in content.split('\n'):
                    info = line.split(' ')
                    info[:] = [x for x in info if x != '']

                    if len(info) > 2:
                        if info[2] == self.device:
                            return info

    ## Returns read and write values
    #  Retreives IO information from '/proc/diskstats' and parses necessary information
    #  @param   self
    #  @return  io      Array containing read and write data
    def getioInfo(self):
        self.lock.acquire()
        io = [self.read, self.write]
        self.lock.release()

        return io

    ## Calculates read and write values in Megabytes
    #  Overrides run() method in Thread
    #  Uses the raw values obtained from self.getioData() function and calculates read and write values
    #  @param     self
    def run(self):
        start = self.getioData()

        while not self.quit:
            sleep(self.sleeptime)
            stop = self.getioData()
            self.lock.acquire()
            # The data is in 512-byte sectors; We divide by 2048 in order to change this into Megabytes
            self.read = (float(stop[5]) - float(start[5])) / 2048
            self.write = (float(stop[9]) - float(start[9])) / 2048
            self.lock.release()
            start = stop

## SSD Module Class
#
class SSD(Module):
    ## Constructor
    #  @param       self
    #  @param       config      Configuration for the instance is going to be created
    def __init__(self, config=None):
        # constructor of the parent class
        super(SSD, self).__init__(config)
        ## RAID device
        self.__raidDev = "/dev/md/raid_unprotected_0"
        ## RAID filesystem mount point
        self.__raidFS = "/mnt/qual"
        ## Location of FIO config file
        self.__fioConf = "/tmp/fio-qual.fio"
        ## Default size partition (GBytes)
        self.partitonsize = 100
        self.loadConfig(attributes=('partitonsize',))
        #  Init the RAID filesystem and store in device for use in collectIO
        device = self.initFS()
        ## Read and Write bandwidth reported by fio tool
        self.readBandwidth = 0.0
        self.writeBandwidth = 0.0
        ## SSD Data collection thread
        #self.collect = collectIO(device)
        #  Start data collection thread
        #self.collect.start()
        #sleep(2)
        #  Create the FIO config file
        self.createFioConfig()
        #  Run FIO to create 100M file
        subprocess.Popen(['fio', self.__fioConf, '--runtime=0']).communicate()
        #  Adding the fio tool thread
        self.addThread(self.runTool)
        #  Adding the message handler
        self.addMsgHandler(SSDRequest, self.handlerMessage)

    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param     self
    #  @param     msg      TZMQ format message
    #  @return    response     A ThalesZMQMessage object
    def handlerMessage(self, msg):
        response = SSDResponse()

        if msg.body.requestType == SSDRequest.STOP:
            self.stop(response)
        elif msg.body.requestType == SSDRequest.RUN:
            self.start(response)
        elif msg.body.requestType == SSDRequest.REPORT:
            self.report(response)
        else:
            self.log.info("Unexpected request")

        return ThalesZMQMessage(response)

    ## Starts running FIO tool
    #
    #  @param     self
    #  @param     response  An SSDResponse object
    def start(self, response):
        subprocess.Popen(['pkill', '-9', 'fio']).communicate()

        if not self._running:
            self.startThread()

        self.report(response)

    ## Stops running FIO tool
    #
    #  @param     self
    #  @param     response  An SSDResponse object
    def stop(self, response):
        self._running = False
        subprocess.Popen(['pkill', '-9', 'fio']).communicate()
        #  Sleep to allow process to die
        sleep(.5)
        self.stopThread()
        self.report(response)
        self.readBandwidth = 0.0
        self.writeBandwidth = 0.0

    ## Reports data from fio tool
    #
    #  @param     self
    #  @param     response  An SSDResponse object
    def report(self, response):
        #info = self.collect.getioInfo()
        response.state = SSDResponse.RUNNING if self._running else SSDResponse.STOPPED
        response.readBandwidth = self.readBandwidth #info[0]
        response.writeBandwidth = self.writeBandwidth #info[1]

    ## Creates the RAID-0
    #
    #  @param   self
    def initFS(self):
        self.log.info('Initializing the SSD file system, this may take some time...')

        # Unmount the filesystem if mounted
        if self.checkIfMounted(self.__raidFS, True):
            self.log.info("Unmounting existing RAID volume")
            self.runCommand('umount %s' % self.__raidFS)

            # Be sure it actually unmounted
            self.checkIfMounted(self.__raidFS, False,
                                failText="Unable to unmount existing RAID volume")

        # Determine which RAID setup script to use
        cwd = os.getcwd()
        makeraid = "mpsinst-makeraid"
        makeraidUSB = "mpsinst-makeraid-usb.sh"
        if os.path.exists("/thales/host/appliances/%s" % makeraid):
            self.log.info("Using system mpsinst-makeraid tool")
            makeraid = "/thales/host/appliances/%s" % makeraid
        elif os.path.exists("%s/%s" % ("qual/modules/ssd", makeraidUSB,)):
            self.log.info("Using debug USB mpsinst-makeraid tool")
            makeraid = "%s/%s" % ("qual/modules/ssd", makeraidUSB,)
        elif os.path.exists("%s/%s" % (cwd, makeraidUSB)):
            self.log.info("Using debug USB mpsinst-makeraid tool")
            makeraid = "%s/%s" % (cwd, makeraidUSB,)
        else:
           raise SSDModuleException("Unable to locate mpsinst-makeraid script")

        # Create the RAID volume using script
        self.log.info("Creating RAID volume (see /tmp/makeraid.log for detail)")
        self.runCommand('%s 10 \"YES,CLEAR_MY_DISKS\" > /tmp/makeraid.log 2>&1' % makeraid,
                        failText='Unable to create RAID volume')

        # Check that RAID volume was successfully created
        if not os.path.exists(self.__raidDev):
            raise SSDModuleException(msg="Unable to create RAID volume")

        # Create the partition
        # TODO: Better way of scripting fdisk than just firing commands at it blindly?
        self.log.info("Creating RAID partition")
        cmd = 'fdisk %s' % self.__raidDev
        self.log.debug(cmd)
        partition = subprocess.Popen(cmd,
                                     stdout=DEVNULL,
                                     stderr=DEVNULL,
                                     shell=True,
                                     stdin=subprocess.PIPE)
        partition.stdin.write('n\n')
        partition.stdin.write('\n')
        partition.stdin.write('\n')
        partition.stdin.write('\n')
        partition.stdin.write('+%sGB\n' % (self.partitonsize,))
        partition.stdin.write('w\n')
        rc = partition.wait()
        self.log.debug("Command return code: %d" % rc)

        # RAID device name is probably a symbolic link
        realDev = os.readlink(self.__raidDev)
        # If it's a relative link, convert it to absolute
        if realDev[0] == '.':
            realDev = os.path.join(os.path.dirname(self.__raidDev), realDev)
        # Save device name so we can return it
        device = os.path.basename(realDev)
        # RAID partition is linked RAID device with "p1" appended
        raidPart = "%sp1" % realDev

        # Check that partition was successfully created - need a bit of a delay before device shows up
        sleep(0.5)
        if not os.path.exists(raidPart):
            # Sleep a bit longer and try again
            self.log.debug("Waiting for device %s to appear..." % raidPart)
            sleep(2)
            if not os.path.exists(raidPart):
                raise SSDModuleException(msg="Unable to create RAID partition")

        # Create the ext4 filesystem and mount it
        self.log.info("Creating RAID filesystem")
        self.runCommand('mkfs.ext4 -q %s' % raidPart,
                        failText='Unable to create RAID filesystem')

        # Create the mount point if not present
        if not os.path.exists(self.__raidFS):
            os.makedirs(self.__raidFS)

        self.log.info("Mounting RAID filesystem")
        self.runCommand('mount -t ext4 --rw %s %s' % (raidPart, self.__raidFS),
                        failText='Unable to mount the RAID partition.')

        # Check that filesystem was successfully mounted
        self.checkIfMounted(self.__raidFS, True,
                            failText='Unable to mount the RAID partition.')

        self.log.info('RAID filesystem initialized.')

        return device

    ## Runs a command, and can raise an exception if the command fails
    #
    #  @param   self
    #  @param   cmd       Command to run (single string, will be run with shell=True)
    #  @param   failText  Text to include in exception; if not provided, exception will not be raised
    def runCommand(self, cmd, failText=''):
        self.log.debug(cmd)
        rc = subprocess.call(cmd,
                             shell=True)
        self.log.debug("Command return code: %d" % rc)
        if rc != 0 and failText != '':
            self.log.error(failText)
            raise SSDModuleException(msg=failText)

    ## Check to see if a filesystem is mounted or not, and raise exception
    #
    #  @param   self
    #  @param   fs        Device name or mount point of filesystem to search for
    #  @param   mounted   Expect filesystem to be mounted or not
    #  @param   failText  Text to include in exception; if not provided, exception will not be raised
    #  @return  True if mounted, False if not
    def checkIfMounted(self, fs, mounted, failText=''):
        self.log.debug("Checking if filesystem %s %s mounted" % (fs, "is" if mounted else "is not"))
        cmd = 'mount | fgrep %s || true' % fs
        #self.log.debug(cmd)
        output = subprocess.check_output(cmd,
                                         shell=True)
        #self.log.debug("Command returned: %s" % output)
        isMounted = output != ''
        if isMounted != mounted and failText != '':
            self.log.error(failText)
            raise SSDModuleException(msg=failText)
        return isMounted

    ## Creates config file for FIO tool
    #
    #  @param   self
    def createFioConfig(self):
        f = open(self.__fioConf, mode='w')
        f.write('[global]\n')
        f.write('rw=rw\n')
        f.write('size=100M\n')
        f.write('\n')
        f.write('[QUAL-SSD]\n')
        f.write('directory=%s\n' % self.__raidFS)

    ## Runs FIO tool
    #
    #  @param   self
    def runTool(self):
        try:
            fio = subprocess.check_output(['fio', self.__fioConf, '--minimal', '--runtime=2'])
            fields = fio.split(';')
            self.readBandwidth = float(fields[6]) / 1024
            self.writeBandwidth = float(fields[47]) / 1024
        except:
            self.log.info("FIO Exited Early")
            pass

    ## Stops background thread
    #
    #  @param     self
    def terminate(self):
        if self._running:
            self._running = False
            subprocess.Popen(['pkill', '-9', 'fio']).communicate()
            self.stopThread()

        #self.collect.quit = True