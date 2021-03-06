import subprocess
import re
import os

from common.module.module import Module, ModuleException
from common.gpb.python.MemoryBandwidth_pb2 import MemoryBandwidthRequest, MemoryBandwidthResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage


## Memory Bandwidth Module Exception Class
class MemoryBandwidthModuleException(ModuleException):
    ## Constructor
    #  @param     self
    #  @param     msg  Message text associated with this exception
    def __init__(self, msg):
        super(MemoryBandwidthModuleException, self).__init__()
        ## Message text associated with this exception
        self.msg = msg


## Memory Bandwidth Module Class
class MemoryBandwidth(Module):
    ## Constructor
    #  @param       self
    #  @param       config      Configuration for the instance is going to be created
    def __init__(self, config=None):
        # constructor of the parent class
        super(MemoryBandwidth, self).__init__(config)
        ## field to save the current Popen object
        self.subProcess = None
        ## field to save the application state
        self.appState = MemoryBandwidthResponse.STOPPED
        ## field to save the last bandwidth read
        self.bandwidth = 0

        ## max memory alloc parameter for pmbw
        self.maxallocmem='-M 10000000'
        ## number of threads parameter for pmbw
        self.numthreads='-P 1'
        ## test array size parameter for pmbw
        self.mSize='-s 1000000'
        self.loadConfig(attributes=('maxallocmem','numthreads','mSize'))

        # adding the message handler
        self.addMsgHandler(MemoryBandwidthRequest, self.hdlrMsg)
        # thread that run PMBW tool
        self.addThread(self.runPmbw)
        # thread that reads the PMBW output
        self.addThread(self.runMemBandwithTest)




    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param     self
    #  @param     memBandwRequest  tzmq format message
    #  @return    response          an MemoryBandwidth Response object
    def hdlrMsg(self, memBandwRequest):
        response = MemoryBandwidthResponse()
        if memBandwRequest.body.requestType == MemoryBandwidthRequest.STOP:
            response = self.stop()
        elif memBandwRequest.body.requestType == MemoryBandwidthRequest.RUN:
            if self.appState == MemoryBandwidthResponse.RUNNING:
                self.stop()
            response = self.start()
        elif memBandwRequest.body.requestType == MemoryBandwidthRequest.REPORT:
            response = self.report()
        else:
            print "Unexpected request"
        return ThalesZMQMessage(response)


    ## Starts running PMBW tool and reading the output
    #
    #  @param     self
    #  @return    a MemoryBandwidth Response object
    def start(self):
        super(MemoryBandwidth, self).startThread()
        self.appState = MemoryBandwidthResponse.RUNNING
        status = MemoryBandwidthResponse()
        status.state = self.appState
        status.memoryBandWidth = self.bandwidth
        return status

    ## Stops running PMBW tool and reading the output
    #
    #  @param     self
    #  @return    a MemoryBandwidth Response object
    def stop(self):
        self._running = False
        subprocess.Popen(["pkill", "-9", "pmbw"])
        self.stopThread()
        self.appState = MemoryBandwidthResponse.STOPPED
        status = MemoryBandwidthResponse()
        status.state = self.appState
        status.memoryBandWidth = self.bandwidth
        self.bandwidth = 0
        return status


    ## Reports the last output of PMBW tool
    #
    #  @param     self
    #  @return    a MemoryBandwidth Response object
    def report(self):
        status = MemoryBandwidthResponse()
        status.state = self.appState
        status.memoryBandWidth = self.bandwidth
        return status

    ## Runs the PMBW tool
    #  @return    None
    def runPmbw(self):
        self.subProcess = subprocess.Popen(["stdbuf", "-o", "L", "pmbw", self.maxallocmem, self.numthreads, self.mSize],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           bufsize=1)
        self.subProcess.wait()

    ## Reads the PMBW tool
    #  @return    None
    def runMemBandwithTest(self):
        if isinstance(self.subProcess, subprocess.Popen):
            line = self.subProcess.stdout.readline()
            if line:
                num = re.search('(?<=bandwidth=).+\t', line)
                self.bandwidth = float(num.group(0))


    ## Stops background thread
    #  @param     self
    def terminate(self):
        if self._running:
            self._running = False
            stop = subprocess.Popen(["pkill", "-9", "pmbw"])
            stop.wait()
            self.stopThread()