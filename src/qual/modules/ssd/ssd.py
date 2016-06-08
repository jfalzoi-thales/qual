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

        ## logs
        self.__log = Logger("SSD Module", level=INFO)
        ## Devices
        self.__dev0 = config['dev0']
        self.__dev1 = config['dev1']
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
                {'dev0':'/dev/sdb1', 'dev1':'/dev/sdc1'},
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
            self.__log.info("Unexpected request")
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
        output = subprocess.check_output('mount | fgrep %s || true' % self.__raidFS,
                                         shell=True)
        if output != '':
            self.__log.info("Unmounting existing RAID filesystem")
            cmd = 'umount %s' % self.__raidFS
            self.__log.debug(cmd)
            unmount = subprocess.Popen(cmd,
                                       stdout=DEVNULL,
                                       shell=True)
            unmount.wait()

            # Be sure it actually unmounted
            output = subprocess.check_output('mount | fgrep %s || true' % self.__raidFS,
                                             shell=True)
            if output != '':
                raise SSDModuleException(msg="Unable to unmount existing RAID volume")

        # Stop RAID configuration and free the devices
        if os.path.exists(self.__raidDev):
            self.__log.info("Deactivating existing RAID volume")
            cmd = 'mdadm --stop %s --quiet' % self.__raidDev
            self.__log.debug(cmd)
            qual0 = subprocess.Popen(cmd,
                                     stdout=DEVNULL,
                                     shell=True)
            qual0.wait()

            self.__log.info("Zeroing RAID component superblocks")
            cmd = 'mdadm --zero-superblock %s %s' % (self.__dev0, self.__dev1,)
            self.__log.debug(cmd)
            subprocess.call(cmd,
                            shell=True)

    ## Creates the RAID-0
    #
    #  @param   self
    def raid0(self):
        # Check that configured RAID component devices exist
        # TODO: Support more than two devices
        if not os.path.exists(self.__dev0):
            raise SSDModuleException(msg="Unable to open Device: %s" % (self.__dev0,))
        elif not os.path.exists(self.__dev1):
            raise SSDModuleException(msg="Unable to open Device: %s" % (self.__dev1,))

        # Check that the configured RAID component devices are not mounted
        output = subprocess.check_output('mount | fgrep %s || true' % self.__dev0,
                                         shell=True)
        if output != '':
            raise SSDModuleException(msg='Configured device %s is already in use' % self.__dev0)
        output = subprocess.check_output('mount | fgrep %s || true' % self.__dev1,
                                         shell=True)
        if output != '':
            raise SSDModuleException(msg='Configured device %s is already in use' % self.__dev1)

        # Zero out beginning of each component device so mdadm doesn't complain
        self.__log.info("Zeroing RAID component headers")
        cmd = "dd if=/dev/zero of=%s bs=512 count=32" % self.__dev0
        self.__log.debug(cmd)
        dd0 = subprocess.Popen(cmd,
                               stderr=DEVNULL,
                               shell=True)
        dd0.wait()

        cmd = "dd if=/dev/zero of=%s bs=512 count=32" % self.__dev1
        self.__log.debug(cmd)
        dd1 = subprocess.Popen(cmd,
                               stderr=DEVNULL,
                               shell=True)
        dd1.wait()

        # Create the RAID volume
        self.__log.info("Creating RAID volume")
        cmd = 'mdadm --create %s --run --quiet --level=stripe --raid-devices=2 %s %s' % \
              (self.__raidDev, self.__dev0, self.__dev1)
        self.__log.debug(cmd)
        raid = subprocess.Popen(cmd,
                                stdout=DEVNULL,
                                shell=True)
        raid.wait()

        # Check that RAID volume was successfully created
        if not os.path.exists(self.__raidDev):
            raise SSDModuleException(msg="Unable to create RAID volume")

        # Create the partition
        self.__log.info("Creating RAID partition")
        cmd = 'fdisk %s' % self.__raidDev
        self.__log.debug(cmd)
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
        self.__log.info("Creating RAID filesystem")
        cmd = 'mkfs.ext4 -q %s' % raidPart
        self.__log.debug(cmd)
        partition = subprocess.Popen(cmd,
                                     stdout=DEVNULL,
                                     shell=True)
        partition.wait()

        if not os.path.exists(self.__raidFS):
            os.makedirs(self.__raidFS)

        self.__log.info("Mounting RAID filesystem")
        cmd = 'mount -t ext4 --rw %s %s' % (raidPart, self.__raidFS)
        self.__log.debug(cmd)
        subprocess.call(cmd,
                        stdout=DEVNULL,
                        shell=True)

        # Check that filesystem was successfully mounted
        output = subprocess.check_output('mount | fgrep %s || true' % self.__raidFS,
                                         shell=True)
        if output == '':
            raise SSDModuleException(msg='Unable to mount the partition.')

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
        self.__log.info('Initializing the SSD file system, this may take some time...')
        # Delete the previous RAID config if exists
        self.deleteConfig()
        # Create the RAID configuration
        self.raid0()
        # log
        self.__log.info('SSD file system initialized.')

        # Create the FIO config file
        self.createFioConfig()
