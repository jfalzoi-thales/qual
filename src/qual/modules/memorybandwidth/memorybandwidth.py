import subprocess
import re

from src.common.module.module import Module
from src.common.gpb.python.MemoryBandwidth_pb2 import MemoryBandwidthRequest, MemoryBandwidthResponse

class MemBandwMsgHdlr(object):
    def __init__(self, memBandwRequest):
        self.msg = memBandwRequest
        super(MemBandwMsgHdlr, self).__init__()
        pass

class MemoryBandwidth(Module):
    def __init__(self, config={}):
        super(MemoryBandwidth, self).__init__(config)
        self.addMsgHandler(MemBandwMsgHdlr, self.start)
        self.addThread(self.runPmbw())
        self.addThread(self.runMemBandwithTest())
        self.subProcess = None
        self.appState = MemoryBandwidthResponse.AppStateT.STOPPED
        self.bandwidth = 0

    @classmethod
    def getConfigurations(cls):
        return [{'maxallocmem': '-M 109951162','numthreads': '-P 1', 'mSize': '-s 109951162'}]

    def hdlrMsg(self, memBandwRequest):
        response = MemoryBandwidthResponse()
        if memBandwRequest.requestType == MemoryBandwidthRequest.STOP:
            response = self.stop()
        elif memBandwRequest.requestType == MemoryBandwidthRequest.RUN:
            response = self.start()
        elif memBandwRequest.requestType == MemoryBandwidthRequest.REPORT:
            response = self.report()
        else:
            print "Unexpected request"
        return response

    def start(self, msg):
        self.M = self.config['maxallocmem']
        self.P = self.config['numthreads']
        self.s = self.config['mSize']
        super(MemoryBandwidth, self).startThread()
        self.appState = MemoryBandwidthResponse.AppStateT.RUNNING
        status = MemoryBandwidthResponse(self.appState, self.lastBandwidthRead)
        return status

    def stop(self):
        self.subProcess.terminate()
        self.appState = MemoryBandwidthResponse.AppStateT.STOPPED
        status = MemoryBandwidthResponse(self.appState, self.lastBandwidthRead)
        return status

    def report(self):
        status = MemoryBandwidthResponse(self.appState, self.lastBandwidthRead)
        return status

    def runPmbw(self):
        while True:
            self.subProcess = subprocess.Popen(["./pmbw", self.M, self.s, self.P],
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)

    def runMemBandwithTest(self):
        while True:
            if isinstance(self.subProcess, subprocess.Popen):
                line = self.subProcess.stdout.readline()
                if not line:
                    continue
                else:
                    num = re.search('(?<=bandwidth=).+\t', line)
                    self.lastBandwidthRead = float(num.group(0))