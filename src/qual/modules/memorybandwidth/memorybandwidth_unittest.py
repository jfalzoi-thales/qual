import unittest
import time
from qual.modules.memorybandwidth.memorybandwidth import MemoryBandwidth
from common.gpb.python.MemoryBandwidth_pb2 import MemoryBandwidthResponse, MemoryBandwidthRequest

# @cond doxygen_unittest

class Test_Rs232(unittest.TestCase):
    def rs232test(self):
        self.module =  MemoryBandwidth(config=MemoryBandwidth.getConfigurations()[0])
        self.module.msgHandler(MemoryBandwidthRequest(MemoryBandwidthRequest.RUN))
        for loop in range(10):
            time.sleep(1)
            status = self.module.msgHandler(MemoryBandwidthRequest(MemoryBandwidthRequest.REPORT))
        self.module.msgHandler(MemoryBandwidthRequest(MemoryBandwidthRequest.STOP))
        pass

if __name__ == '__main__':
    unittest.main()

## @endcond
