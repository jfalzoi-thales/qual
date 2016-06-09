import unittest
from time import sleep
import arinc717
from common.gpb.python.ARINC717Frame_pb2 import ARINC717FrameRequest
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

#  @cond doxygen_unittest

## ARINC717 Messages
class ARINC717Messages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "ARINC 717"

    @staticmethod
    def getMenuItems():
        return [("Report",  ARINC717Messages.report),]

    @staticmethod
    def report():
        message = ARINC717FrameRequest()
        message.requestType = ARINC717FrameRequest.REPORT
        return message

## ARINC717 Unit Test
class Test_ARINC717(unittest.TestCase):
    def test_basic(self):
        log = Logger(name='Test ARINC717')
        log.info('Running functionality test for ARINC717 module:')
        self.module = arinc717.ARINC717()

        log.info("REPORT current ARINC717 Frame information:")
        self.module.msgHandler(ThalesZMQMessage(ARINC717Messages.report()))
        sleep(1)

        log.info("REPORT current ARINC717 Frame information again:")
        self.module.msgHandler(ThalesZMQMessage(ARINC717Messages.report()))

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond