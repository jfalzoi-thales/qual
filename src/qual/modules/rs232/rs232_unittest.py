import unittest
import time
from qual.modules.rs232.rs232 import Rs232
from common.gpb.python.RS232_pb2 import RS232Request, RS232Response

# @cond doxygen_unittest

class Test_Rs232(unittest.TestCase):
    def rs232test(self):
        self.module =  Rs232(config=Rs232.getConfigurations()[0])
        self.module.msgHandler(RS232Request(RS232Request.RUN))
        for loop in range(10):
            time.sleep(1)
            status = self.module.msgHandler(RS232Request(RS232Request.REPORT))
        self.module.msgHandler(RS232Request(RS232Request.STOP))
        pass

if __name__ == '__main__':
    unittest.main()

## @endcond
