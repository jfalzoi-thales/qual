import subprocess
import os
import time

from common.module.module import Module
from common.gpb.python.SSD_pb2 import SSDRequest, SSDResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger, DEBUG
from qual.modules.ssd.ssd_Exception import SSDDeviceException

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
        self.log = Logger("SSD Module", level=DEBUG)
        ## Devices
        self.dev0 = config['dev0']
        self.dev1 = config['dev1']
        ## Init the File System
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
    #  @return    response          an RS-232 Response object
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

    ## Starts sending and reading data through RS-232
    #
    #  @param     self
    #  @return    self.report() a RS-232 Response object
    def start(self):
        super(SSD, self).startThread()
        self.state = SSDResponse.RUNNING
        status = SSDResponse()
        status.state = self.state
        return status

    ## Stops sending and reading data through RS-232
    #
    #  @param     self
    #  @return    self.report() a RS-232 Response object
    def stop(self):
        self._running = False
        stop = subprocess.Popen(['pkill', '-9', 'fio'])
        stop.wait()
        self.state = SSDResponse.STOPPED
        status = SSDResponse()
        self.stopThread()
        status.state = self.state
        return status


    ## unmount and delete partition
    def deleteConfig(self):
        ## unmount the partition if exists
        output = subprocess.check_output('df -h | grep qual || true', shell=True)
        if output != '':
            unmount = subprocess.Popen('umount -l /mnt/qual', shell=True)
            unmount.wait()

        ## Delete partitionif exists
        output = subprocess.check_output('ls /dev/ | grep md0p1 ||true', shell=True)
        if output != '':
            output = subprocess.Popen('fdisk /dev/md0', stdin=subprocess.PIPE, shell=True)
            output.stdin.write('d\n')
            output.stdin.write('w\n')

        ## stop RAID configuration and free the devices
        output = subprocess.check_output('ls /dev/ | grep md0 ||true', shell=True)
        if output != '':
            md0 = subprocess.Popen('mdadm --stop /dev/md0', shell=True)
            md0.wait()
            subprocess.call('mdadm --zero-superblock %s %s' % (self.dev0, self.dev1,), shell=True)

    ## Create the RAID-0
    def raid0(self):
        if not os.path.exists(self.dev0):
            raise SSDDeviceException(device=self.dev0)
        elif not os.path.exists(self.dev1):
            raise SSDDeviceException(device=self.dev1)
        else:
            ## Create the RAID config
            raid = subprocess.Popen('mdadm --create --verbose /dev/md0 --level=stripe --raid-devices=2 %s %s' % (self.dev0, self.dev1,),
                                    shell=True,
                                    stdin=subprocess.PIPE)
            raid.stdin.write('y\n')
            raid.wait()
            ## Create the partition
            partition = subprocess.Popen('fdisk /dev/md0', shell=True, stdin=subprocess.PIPE)
            partition.stdin.write('n\n')
            partition.stdin.write('\n')
            partition.stdin.write('\n')
            partition.stdin.write('\n')
            partition.stdin.write('\n')
            partition.stdin.write('w\n')
            partition.wait()
            ## Mount the partition with ext4
            partition = subprocess.Popen('mkfs.ext4 /dev/md0p1', shell=True)
            partition.wait()
            if not os.path.exists('/mnt/qual'):
                os.makedirs('/mnt/qual')
            subprocess.call('mount -t ext4 --rw /dev/md0p1 /mnt/qual', shell=True)

    def runTool(self):
        sub = subprocess.Popen('fio ../modules/ssd/fio-qual.fio', shell=True)
        sub.wait()

    ## Function to init the File System
    def initFS(self):
        ## Delete the prvious config if exists
        self.deleteConfig()
        ## Create the configuration
        self.raid0()
        ## log
        self.log.info('File system initialized.')