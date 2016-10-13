import os
import subprocess
from time import sleep

from common.pb2.ErrorMessage_pb2 import ErrorMessage
from qual.pb2.SSD_pb2 import SSDRequest, SSDResponse
from ssd_Exception import SSDModuleException
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage

## Discard the output
DEVNULL = open(os.devnull, 'wb')

## SSD Module Class
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
        self.__raidFS = ""
        ## Location of FIO config file
        self.__fioConf = "/tmp/fio-qual.fio"
        ## Whether or not to format the RAID at startup
        self.formatRAID = True
        ## Default size partition (GBytes)
        self.partitionsize = 100
        self.loadConfig(attributes=('partitionsize', 'formatRAID'))
        ## Read and Write bandwidth reported by fio tool
        self.readBandwidth = 0.0
        self.writeBandwidth = 0.0

        # If TSP Download or Qual test filesystem is present, use instead of formatting RAID
        tspDownloadFS = "/tsp-download"
        qualTestFS    = "/mnt/qual"
        if self.checkIfMounted(tspDownloadFS):
            self.log.info("Using TSP download partition for SSD test")
            self.__raidFS = tspDownloadFS
            self.runCommand('rm -rf %s/*' % tspDownloadFS,
                            failText='Unable to clean up TSP download directory')
        elif self.checkIfMounted(qualTestFS):
            self.log.info("Using existing %s filesystem for SSD test", qualTestFS)
            self.__raidFS = qualTestFS
        else:
            # If LVM volumes exist, we don't want to mess with the RAID
            output = subprocess.check_output('lvs || true', shell=True)
            if output:
                self.log.warning("RAID appears to be in use; disabling SSD test")
            else:
                # Go ahead and format the RAID
                self.__raidFS = qualTestFS
                self.initFS()

        if self.__raidFS:
            #  Create the FIO config file
            self.createFioConfig()
            #  Run FIO to create test file
            self.log.info("Creating FIO test files...")
            self.runCommand('fio %s --runtime=0 > /tmp/fiosetup.log 2>&1' % self.__fioConf,
                            failText='Unable to create FIO test files')

        #  Adding the fio tool thread
        self.addThread(self.runTool)
        #  Adding the message handler
        self.addMsgHandler(SSDRequest, self.handlerMessage)

    ## Handles incoming messages
    #  Receives tzmq request and runs requested process
    #  @param     self
    #  @param     msg      TZMQ format message
    #  @return    response     A ThalesZMQMessage object
    def handlerMessage(self, msg):
        # If raidFS is empty, we're disabled because SSD RAID is in use (requirement MPS-SRS-2334).
        # If partition is not mounted, someone probably used the "SSD Erase" command.
        # Either way, we can't do anything, so return an error message.
        if not self.__raidFS or not self.checkIfMounted(self.__raidFS):
            errorMessage = ErrorMessage()
            errorMessage.error_code = 1010
            if self.__raidFS:
                errorMessage.error_description = "SSD test not available: partition removed"
            else:
                errorMessage.error_description = "SSD test not available: SSD RAID in use"
            return ThalesZMQMessage(errorMessage)

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
    #  @param     self
    #  @param     response  An SSDResponse object
    def start(self, response):
        subprocess.call(['pkill', '-9', 'fio'])

        if not self._running:
            self.startThread()

        self.report(response)

    ## Stops running FIO tool
    #  @param     self
    #  @param     response  An SSDResponse object
    def stop(self, response):
        self._running = False
        subprocess.call(['pkill', '-9', 'fio'])
        #  Sleep to allow process to die
        sleep(.5)
        self.stopThread()
        self.report(response)
        self.readBandwidth = 0.0
        self.writeBandwidth = 0.0

    ## Reports data from fio tool
    #  @param     self
    #  @param     response  An SSDResponse object
    def report(self, response):
        response.state = SSDResponse.RUNNING if self._running else SSDResponse.STOPPED
        response.readBandwidth = self.readBandwidth
        response.writeBandwidth = self.writeBandwidth

    ## Creates the RAID-0
    #  @param   self
    def initFS(self):
        self.log.info('Initializing the SSD file system, this may take some time...')

        # Unmount the filesystem if mounted
        if self.checkIfMounted(self.__raidFS):
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
        partition.stdin.write('+%sGB\n' % (self.partitionsize,))
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
    #  @param   self
    #  @param   fs        Device name or mount point of filesystem to search for
    #  @param   mounted   Expect filesystem to be mounted or not
    #  @param   failText  Text to include in exception; if not provided, exception will not be raised
    #  @return  True if mounted, False if not
    def checkIfMounted(self, fs, mounted=True, failText=''):
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
    #  @param   self
    def createFioConfig(self):
        f = open(self.__fioConf, mode='w')
        f.write('[global]\n')
        f.write('size=960M\n')
        f.write('ioengine=libaio\n')
        f.write('iodepth=4\n')
        f.write('bs=1M\n')
        f.write('direct=1\n')
        f.write('\n')
        f.write('[READ]\n')
        f.write('stonewall\n')
        f.write('new_group\n')
        f.write('directory=%s\n' % self.__raidFS)
        f.write('rw=read\n')
        f.write('\n')
        f.write('[WRITE]\n')
        f.write('stonewall\n')
        f.write('new_group\n')
        f.write('directory=%s\n' % self.__raidFS)
        f.write('rw=write\n')

    ## Runs FIO tool
    #  @param   self
    def runTool(self):
        try:
            fio = subprocess.check_output(['fio', self.__fioConf, '--minimal', '--runtime=2'])
            for line in fio.splitlines():
                fields = line.split(';')
                if fields[2] == "WRITE":
                    self.writeBandwidth = float(fields[47]) / 1024
                else:
                    self.readBandwidth = float(fields[6]) / 1024
        except:
            self.log.info("FIO Exited Early" if self._running else "FIO Stopped")
            pass

    ## Stops background thread
    #  @param     self
    def terminate(self):
        if self._running:
            self._running = False
            subprocess.call(['pkill', '-9', 'fio'])
            self.stopThread()
