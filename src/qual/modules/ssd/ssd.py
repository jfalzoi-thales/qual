import subprocess
import os
import time

from common.module.module import Module
from common.gpb.python.SSD_pb2 import SSDRequest, SSDResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger, DEBUG, INFO
from qual.modules.ssd.ssd_Exception import SSDModuleException

## Discard the output
DEVNULL = open(os.devnull, 'wb')

## RS-232 Class Module
#
class SSD(Module):
    ## Constructor
    #  @param       self
    #  @param       config      Configuration for the instance is going to be created
    def __init__(self, config={}):
        # constructor of the parent class
        super(SSD, self).__init__(config)

        ## Devices
        self.__devices = config['devices']
        ## RAID device
        self.__raidDev = "/dev/md/qual0"
        ## RAID filesystem mount point
        self.__raidFS = "/mnt/qual"
        ## Location of FIO config file
        self.__fioConf = "/tmp/fio-qual.fio"
        ## Application state
        self.state = SSDResponse.STOPPED

        # Init the required File System
        self.initFS()
        # adding the thread
        self.addThread(self.runTool)
        # adding the message handler
        self.addMsgHandler(SSDRequest, self.handlerMessage)

    @classmethod
    ## Returns the test configurations for that module
    #
    #  @return      test configurations
    def getConfigurations(cls):
        return [
                {'devices':('/dev/sdb1', '/dev/sdc1', '/dev/sdd1', '/dev/sde1')},
                ]

    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param     self
    #  @param     rs232Request      tzmq format message
    #  @return    response          an SSD Response object
    def handlerMessage(self, request):
        response = SSDResponse()
        if request.body.requestType == SSDRequest.STOP:
            response = self.stop()
        elif request.body.requestType == SSDRequest.RUN:
            if self.state == SSDResponse.RUNNING:
                self.stop()
            response = self.start()
        else:
            self.log.info("Unexpected request")
        return ThalesZMQMessage(response)

    ## Starts running FIO tool
    #
    #  @param     self
    #  @return    self.report() a SSD Response object
    def start(self):
        super(SSD, self).startThread()
        self.state = SSDResponse.RUNNING
        status = SSDResponse()
        status.state = self.state
        return status

    ## Stops running FIO tool
    #
    #  @param     self
    #  @return    self.report() a SSD Response object
    def stop(self):
        self._running = False
        stop = subprocess.Popen(['pkill', '-9', 'fio'],
                                stdout=DEVNULL,
                                stderr=DEVNULL)
        stop.wait()
        self.state = SSDResponse.STOPPED
        status = SSDResponse()
        self.stopThread()
        status.state = self.state
        return status


    ## Unmount and delete partition
    #
    #  @param   self
    def deleteConfig(self):
        # Unmount the filesystem if mounted
        if self.checkIfMounted(self.__raidFS, True):
            self.log.info("Unmounting existing RAID volume")
            self.runCommand('umount %s' % self.__raidFS)

            # Be sure it actually unmounted
            self.checkIfMounted(self.__raidFS, False,
                                failText="Unable to unmount existing RAID volume")

        # Stop RAID configuration and free the devices
        if os.path.exists(self.__raidDev):
            self.log.info("Deactivating existing RAID volume")
            self.runCommand('mdadm --stop %s --quiet' % self.__raidDev,
                            failText="Unable to deactivate existing RAID volume")

            self.log.info("Zeroing RAID component superblocks")
            for dev in self.__devices:
                self.runCommand('mdadm --zero-superblock %s' % dev)

    ## Creates the RAID-0
    #
    #  @param   self
    def raid0(self):
        self.log.info('Initializing the SSD file system, this may take some time...')

        # Zero out beginning of each component device so mdadm doesn't complain
        self.log.info("Zeroing RAID component headers")
        for dev in self.__devices:
            self.runCommand("dd if=/dev/zero of=%s bs=512 count=32 status=none" % dev)

        # Create the RAID volume
        self.log.info("Creating RAID volume")
        self.runCommand('mdadm --create %s --run --quiet --level=stripe --raid-devices=%d %s' % \
                        (self.__raidDev, len(self.__devices), " ".join(self.__devices)),
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
        partition.stdin.write('\n')
        partition.stdin.write('w\n')
        partition.wait()

        # RAID partition is RAID device with "p1" appended
        raidPart = "%sp1" % self.__raidDev

        # Check that partition was successfully created - need a bit of a delay before device shows up
        time.sleep(0.25)
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

    ## Runs a command, and can raise an exception if the command fails
    #
    #  @param   self
    #  @param   cmd       Command to run (single string, will be run with shell=True)
    #  @param   failText  Text to include in exception; if not provided, exception will not be raised
    def runCommand(self, cmd, failText=''):
        self.log.debug(cmd)
        rc = subprocess.call(cmd,
                             stdout=DEVNULL,
                             shell=True)
        self.log.debug("Command return code: %d" % rc)
        if rc != 0 and failText != '':
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
        self.log.debug(cmd)
        output = subprocess.check_output(cmd,
                                         shell=True)
        self.log.debug("Command returned: %s" % output)
        isMounted = output != ''
        if isMounted != mounted and failText != '':
            raise SSDModuleException(msg=failText)
        return isMounted

    ## Creates config file for FIO tool
    #
    #  @param   self
    def createFioConfig(self):
        f = open(self.__fioConf, mode='w')
        f.write('[global]\n')
        f.write('rw=randrw\n')
        f.write('size=1024m\n')
        f.write('\n')
        f.write('[QUAL-SSD]\n')
        f.write('directory=%s\n' % self.__raidFS)

    ## Runs FIO tool
    #
    #  @param   self
    def runTool(self):
        sub = subprocess.Popen(['fio', self.__fioConf],
                               stdout=DEVNULL,
                               stderr=DEVNULL)
        sub.wait()

    ## Inits the requierd File System
    #
    #  @param   self
    def initFS(self):
        # Check that configured RAID component devices exist
        for dev in self.__devices:
            if not os.path.exists(dev):
                raise SSDModuleException(msg="Configured device %s not present" % dev)

        # Check that the configured RAID component devices are not mounted
        for dev in self.__devices:
            self.checkIfMounted(dev, False,
                                failText='Configured device %s is already in use' % dev)

        # Delete the previous RAID config if exists
        self.deleteConfig()
        # Create the RAID configuration
        self.raid0()
        # log
        self.log.info('SSD file system initialized.')

        # Create the FIO config file
        self.createFioConfig()
