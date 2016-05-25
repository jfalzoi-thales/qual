import unittest
from rs232 import *

class Test_Rs232(unittest.TestCase):
    def rs232test(self, port):
        self.module =  Rs232(config=Rs232.getConfigurations()[0])
        self.module.msgHandler(StartMessage(port))
        for loop in range(20):
            time.sleep(1)
            status = self.module.msgHandler(RequestReportMessage())
            print "Status reported as match=" + str(status.match) + ", mismatch=" + str(status.mismatch)
        self.module.msgHandler(StopMessage())
        pass

if __name__ == '__main__':
    unittest.main()