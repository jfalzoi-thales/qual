import unittest
import time
from rs232 import *

class Test_Rs232(unittest.TestCase):
    def rs232test(self):
        ports = PortMsg("port': /dev/ttyUSB1", "port': /dev/ttyUSB2")
        self.module =  Rs232(config=Rs232.getConfigurations()[0])
        self.module.msgHandler(StartMessage(ports))
        for loop in range(1000):
            time.sleep(5)
            status = self.module.msgHandler(RequestReportMessage())
        self.module.msgHandler(StopMessage())