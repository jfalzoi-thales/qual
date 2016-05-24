import subprocess
import os
import re

from src.common.module.module import Module
from src.common.gpb.python.baseMessage import BaseMessage
import threading

# Variable for PMBW process
pmbwOutput = None

class StartMessage(BaseMessage):
    def __init__(self):
        super(StartMessage, self).__init__()


class StopMessage(BaseMessage):
    def __init__(self):
        super(StopMessage, self).__init__()
        pass


class RequestReportMessage(BaseMessage):
    def __init__(self, bandwidth):
        super(RequestReportMessage, self).__init__()
        pass


class StatusRequestMessage(BaseMessage):
    def __init__(self, bandwidth):
        self.bandwidth = bandwidth
        super(StatusRequestMessage, self).__init__()
        pass


class MemoryBandwidth(Module):
    def __init__(self, config={}):
        super(MemoryBandwidth, self).__init__(config)
        self.addMsgHandler(StartMessage, self.start)
        self.addMsgHandler(StopMessage, self.stop)
        self.addMsgHandler(RequestReportMessage, self.report)
        self.addThread(self.runPmbw())
        self.addThread(self.runMemBandwithTest())
        self.PMBW = "pmbw"
        self.bandwidth = []
        self.lastBandwidthRead = 0

    # These configurations are the most common,
    # mSize == 0, means no max size in memory reservation
    @classmethod
    def getConfigurations(cls):
        return [{'numThreads': 1, 'mSize': 1024},
                {'numThreads': 1, 'mSize': 0}]

    def start(self, msg):
        super(MemoryBandwidth, self).startThread()
        status = StatusRequestMessage(self.lastBandwidthRead)
        return status

    def stop(self):
        global pmbwOutput
        pmbwOutput.terminate()
        status = StatusRequestMessage(self.lastBandwidthRead)
        super(MemoryBandwidth, self).stopThread()
        return status

    def report(self):
        status = StatusRequestMessage(self.lastBandwidthRead)
        return status

    def runPmbw(self):
        global pmbwOutput
        while True:
            pmbwOutput= subprocess.Popen(
                        self.PMBW,
                        stdout=subprocess.PIPE)

    def runMemBandwithTest(self):
        global pmbwOutput
        while True:
            line = pmbwOutput.stdout.readline()
            if not line:
                continue
            else:
                num = re.search('(?<=bandwidth=).+\t', line)
                self.bandwidth.append(float(num.group(0)))
                self.lastBandwidthRead = float(num.group(0))