import unittest
import time
from memorybandwidth import MemoryBandwidth, StartMessage, RequestReportMessage, StopMessage


class Test_MemoryBandwidth(unittest.TestCase):
    def __init__(self):
        self.module = MemoryBandwidth(MemoryBandwidth.getConfigurations()[0])
        self.module.msgHandler(StartMessage())
        for iter in range(100):
            time.sleep(10)
            status = self.module.msgHandler(RequestReportMessage())
        self.module.msgHandler(StopMessage())