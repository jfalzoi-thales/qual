import subprocess
import re

from common.module.module import Module
from common.logger.logger import Logger
from common.gpb.python.MemoryBandwidth_pb2 import MemoryBandwidthRequest, MemoryBandwidthResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage

## MemoryBandwidth Class Module
#
class MemoryBandwidth(Module):
    ## Constructor
    #  @param       self
    #  @param       config      Configuration for the instance is going to be created
    def __init__(self, config={}):
        ## constructor of the parent class
        super(MemoryBandwidth, self).__init__(config)
        ## adding the message handler
        self.addMsgHandler(MemoryBandwidthRequest, self.hdlrMsg)
        ## thread that run PMBW tool
        self.addThread(self.runPmbw)
        ## thread that reads the PMBW output
        self.addThread(self.runMemBandwithTest)
        ## field to save the current Popen object
        self.subProcess = None
        ## Logger
        self.log = Logger("Test Memory Bandwith")
        ## field to save the application state
        self.appState = MemoryBandwidthResponse.STOPPED
        ## field to save the last bandwidth read
        self.bandwidth = 0

    @classmethod
    ## Returns the test configurations for that module
    #
    #  @return      test configurations
    def getConfigurations(cls):
        return [{'maxallocmem': '-M 10000000','numthreads': '-P 1', 'mSize': '-s 10000000'}]

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


    ## Starts runnung PMBW tool and reading the output
    #
    #  @param     self
    #  @param     msg  tzmq format message
    #  @return    self.report() a MemoryBandwidth Response object
    def start(self):
        self.M = self.config['maxallocmem']
        self.P = self.config['numthreads']
        self.s = self.config['mSize']
        super(MemoryBandwidth, self).startThread()
        self.appState = MemoryBandwidthResponse.RUNNING
        status = MemoryBandwidthResponse()
        status.state = self.appState
        status.memoryBandWidth = self.bandwidth
        return status

    ## Stops runnung PMBW tool and reading the output
    #
    #  @param     self
    #  @return    self.report() a MemoryBandwidth Response object
    def stop(self):
        self._running = False
        subprocess.Popen(["sudo", "pkill", "-9", "pmbw"])
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
    #  @return    self.report() a MemoryBandwidth Response object
    def report(self):
        status = MemoryBandwidthResponse()
        status.state = self.appState
        status.memoryBandWidth = self.bandwidth
        return status

    ## Runs the PMBW tool
    #  @return    None
    def runPmbw(self):
        self.subProcess = subprocess.Popen(["stdbuf", "-o", "L","/usr/local/bin/pmbw", self.M, self.s, self.P],
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