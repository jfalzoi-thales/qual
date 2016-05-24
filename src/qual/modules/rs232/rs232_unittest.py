import unittest
from rs232 import Rs232, PortMsg

class Test_Rs232(unittest.TestCase):
    def rs232test(self):
        ports = PortMsg("port': '/dev/ttyUSB1", "port': '/dev/ttyUSB2")
        self.module =  Rs232(config=Rs232.getConfigurations()[0])