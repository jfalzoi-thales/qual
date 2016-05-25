import unittest
from rs232 import *
from src.common.module.module import Module
from src.common.module.unitTest import BaseMessage
from src.common.gpb.python.RS232_pb2 import RS232Request, RS232Response

class Test_Rs232(unittest.TestCase):
    def rs232test(self, port):
        msgStart = RS232Request.RUN
        msgReport = RS232Request.REPORT
        msgStop = RS232Request.STOP
        self.module =  Rs232(config=Rs232.getConfigurations()[0])
        self.module.msgHandler(Rs232MsgHdlr(msgStart))
        for loop in range(10):
            time.sleep(1)
            status = self.module.msgHandler(Rs232MsgHdlr(msgReport))
        self.module.msgHandler(Rs232MsgHdlr(msgStop))
        pass

if __name__ == '__main__':
    unittest.main()