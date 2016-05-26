import unittest
import time
from memorybandwidth import *
from src.common.gpb.python.MemoryBandwidth_pb2 import MemoryBandwidthResponse, MemoryBandwidthRequest

class Test_Rs232(unittest.TestCase):
    def rs232test(self):
        msgStart = MemoryBandwidthRequest.RUN
        msgReport = MemoryBandwidthRequest.REPORT
        msgStop = MemoryBandwidthRequest.STOP
        self.module =  MemoryBandwidth(config=MemoryBandwidth.getConfigurations()[0])
        self.module.msgHandler(MemBandwMsgHdlr(msgStart))
        for loop in range(10):
            time.sleep(1)
            status = self.module.msgHandler(MemBandwMsgHdlr(msgReport))
        self.module.msgHandler(MemBandwMsgHdlr(msgStop))
        pass

if __name__ == '__main__':
    unittest.main()