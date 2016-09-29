import re
import subprocess
from time import sleep

from qual.pb2.MemoryBandwidth_pb2 import MemoryBandwidthRequest, MemoryBandwidthResponse
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


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
        self.startThread()
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
        self.subProcess.communicate()
        self.subProcess = None

    ## Reads the PMBW tool
    #  @return    None
    def runMemBandwithTest(self):
        if isinstance(self.subProcess, subprocess.Popen):
            line = self.subProcess.stdout.readline()
            if line:
                num = re.search('(?<=bandwidth=).+\t', line)
                self.bandwidth = float(num.group(0))
        else:
            sleep(0.1)

    ## Stops background thread
    #  @param     self
    def terminate(self):
        if self._running:
            self._running = False
            stop = subprocess.Popen(["pkill", "-9", "pmbw"])
            stop.wait()
            self.stopThread()
