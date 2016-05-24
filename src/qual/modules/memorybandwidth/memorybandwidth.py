import subprocess
import os
import re

from src.common.module.module import Module
from src.common.gpb.python.baseMessage import BaseMessage
from threading import Thread


class StartMessage(BaseMessage):
    def __init__(self):
        super(StartMessage, self).__init__()


class StopMessage(BaseMessage):
    def __init__(self):
        super(StopMessage, self).__init__()
        pass


class RequestReportMessage(BaseMessage):
    def __init__(self, bandwidth):
        self.bandwidth = bandwidth
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
        self.addThread(self.runMemBandwithTest())
        self.PMBW = "pmbw"
        self.bandwidth = []
        self.averageBandwidth = self.aveBandwidth()

    # This configurations are the most common,
    # mSize == 0, means no max size in memory reservation
    @classmethod
    def getConfigurations(cls):
        return [{'numThreads': 1, 'mSize': 1024},
                {'numThreads': 1, 'mSize': 0}]

    def start(self, msg):
        super(MemoryBandwidth, self).startThread()
        status = StatusRequestMessage(self.aveBandwidth())
        return status

    def stop(self):
        status = StatusRequestMessage(self.aveBandwidth())
        super(MemoryBandwidth, self).stopThread()
        return status

    def report(self):
        status = StatusRequestMessage(self.aveBandwidth())
        return status

    #   pmbw with the required parameters:
    #   Runs the pmbw and creates a file called "stats.txt"
    #   with all statistics of the test
    def runMemBandwithTest(self):
        while True:
            subprocess.call([self.PMBW, "-S " + str(self.config['mSize']), "-P " + str(self.config['numThreads'])])
            self.parseOutput()

    # parse the output test
    #   parse the output test called "stats.txt"
    #   if file, returns a list with all the calculated bandwidth
    #   if no file, returns an empty list
    def parseOutput(self):
        statsFile = "stats.txt"
        if os.path.exists(statsFile):
            file = open(statsFile)
            for line in file:
                num = re.search('(?<=bandwidth=).+\t', line)
                self.bandwidth.append(float(num.group(0)[:-1]))
        else:
            return []

    # returns the max bandwidth of the test
    def maxBandwidth(self):
        return max(self.bandwidth)

    # returns the min bandwidth of the test
    def minBandwidth(self):
        return min(self.bandwidth)

    # returns the average bandwidth of the test
    def aveBandwidth(self):
        return sum(self.bandwidth) / len(self.bandwidth) if (len(self.bandwidth) > 0) else 0