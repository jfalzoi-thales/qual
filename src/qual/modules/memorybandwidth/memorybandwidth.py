import subprocess
import re

from common.module.module import Module
from common.gpb.python.MemoryBandwidth_pb2 import MemoryBandwidthRequest, MemoryBandwidthResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage

class MemoryBandwidth(Module):
    def __init__(self, config={}):
        super(MemoryBandwidth, self).__init__(config)
        self.addMsgHandler(MemoryBandwidthRequest, self.hdlrMsg)
        self.addThread(self.runPmbw)
        self.addThread(self.runMemBandwithTest)
        self.subProcess = None
        self.appState = MemoryBandwidthResponse.AppStateT.STOPPED
        self.bandwidth = 0

    @classmethod
    def getConfigurations(cls):
        return [{'maxallocmem': '-M 109951162','numthreads': '-P 1', 'mSize': '-s 109951162'}]

    def hdlrMsg(self, memBandwRequest):
        response = MemoryBandwidthResponse()
        if memBandwRequest.body.requestType == MemoryBandwidthRequest.STOP:
            response = self.stop()
        elif memBandwRequest.body.requestType == MemoryBandwidthRequest.RUN:
            response = self.start()
        elif memBandwRequest.body.requestType == MemoryBandwidthRequest.REPORT:
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
        return ThalesZMQMessage(status)

    def stop(self):
        subprocess.Popen(["sudo", "pkill", "-9", "pmbw"])
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