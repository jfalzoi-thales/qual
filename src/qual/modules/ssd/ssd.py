import subprocess
import os
import time

from common.module.module import Module
from common.gpb.python.SSD_pb2 import SSDRequest, SSDResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger, DEBUG
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
        ## constructor of the parent class
        super(SSD, self).__init__(config)
        ## logs
        self.__log = Logger("SSD Module", level=DEBUG)
        ## Devices
        self.__dev0 = config['dev0']
        self.__dev1 = config['dev1']
        ## Init the requierd File System
        self.initFS()
        ## adding the thread
        self.addThread(self.runTool)
        ## adding the message handler
        self.addMsgHandler(SSDRequest, self.handlerMessage)
        ## init the application state
        self.state = SSDResponse.STOPPED

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
        elif request.body.requestType == SSDRequest.REPORT:
            response = self.report()
        else:
            print "Unexpected request"
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
        ## unmount the partition if exists
        output = subprocess.check_output('df -h | grep qual || true',
                                         shell=True)
        if output != '':
            unmount = subprocess.Popen('umount -l /mnt/qual',
                                       stdout=DEVNULL,
                                       stderr=DEVNULL, shell=True)
            unmount.wait()

        ## Delete partitionif exists
        output = subprocess.check_output('ls /dev/ | grep md0p1 ||true', shell=True)
        if output != '':
            output = subprocess.Popen('fdisk /dev/md0',
                                      stdout=DEVNULL,
                                      stderr=DEVNULL,
                                      stdin=subprocess.PIPE,
                                      shell=True)
            output.stdin.write('d\n')
            output.stdin.write('w\n')

        ## stop RAID configuration and free the devices
        output = subprocess.check_output('ls /dev/ | grep md0 ||true', shell=True)
        if output != '':
            md0 = subprocess.Popen('mdadm --stop /dev/md0',
                                   stdout=DEVNULL,
                                   stderr=DEVNULL,
                                   shell=True)
            md0.wait()
            subprocess.call('mdadm --zero-superblock %s %s' % (self.__dev0, self.__dev1,), shell=True)

    ## Creates the RAID-0
    #
    #  @param   self
    def raid0(self):
        if not os.path.exists(self.__dev0):
            raise SSDModuleException(msg="Unable to open Device: %s" % (self.__dev0,))
        elif not os.path.exists(self.__dev1):
            raise SSDModuleException(msg="Unable to open Device: %s" % (self.__dev1,))
        else:
            ## Create the RAID config
            raid = subprocess.Popen('mdadm --create --verbose /dev/md0 --level=stripe --raid-devices=2 %s %s' % (self.__dev0, self.__dev1,),
                                    stdout=DEVNULL,
                                    stderr=DEVNULL,
                                    shell=True,
                                    stdin=subprocess.PIPE)
            raid.stdin.write('y\n')
            raid.wait()

            ## Create the partition
            partition = subprocess.Popen('fdisk /dev/md0',
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

            ## Mount the partition with ext4
            partition = subprocess.Popen('mkfs.ext4 /dev/md0p1',
                                         stdout=DEVNULL,
                                         stderr=DEVNULL,
                                         shell=True)
            partition.wait()
            if not os.path.exists('/mnt/qual'):
                os.makedirs('/mnt/qual')
            try:
                subprocess.call('mount -t ext4 --rw /dev/md0p1 /mnt/qual',
                                 stdout=DEVNULL,
                                 stderr=DEVNULL,
                                 shell=True)
            except subprocess.CalledProcessError:
                raise SSDModuleException(msg='Unable to mount the partition.')

    ## Runs FIO tool
    #
    #  @param   self
    def runTool(self):
        sub = subprocess.Popen('fio ../modules/ssd/fio-qual.fio',
                               stdout=DEVNULL,
                               stderr=DEVNULL,
                               shell=True)
        sub.wait()

    ## Inits the requierd File System
    #
    #  @param   self
    def initFS(self):
        self.__log.info('Starting the SSD File System, this may take several minutes...')
        ## Delete the prvious config if exists
        self.deleteConfig()
        ## Create the configuration
        self.raid0()
        ## log
        self.__log.info('File system initialized.')