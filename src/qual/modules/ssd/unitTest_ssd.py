import unittest

from time import sleep
from common.gpb.python.SSD_pb2 import SSDRequest, SSDResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages
from qual.modules.ssd.ssd import SSD

# @cond doxygen_unittest

## SSD Messages
class SSDMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "SSD"

    @staticmethod
    def getMenuItems():
        return [("Run",     SSDMessages.run),
                ("Stop",    SSDMessages.stop)]

    @staticmethod
    def run():
        message = SSDRequest()
        message.requestType = SSDRequest.RUN
        return message

    @staticmethod
    def stop():
        message = SSDRequest()
        message.requestType = SSDRequest.STOP
        return message


## SSD Unit Test
class Test_SSD(unittest.TestCase):
    ## Basic functionality test for SSD module
    #  @param     self
    def test_basic(self):
        log = Logger(name='SSD Module Test')
        self.module = SSD(config=SSD.getConfigurations()[0])

        log.info("RUN FIO tool")
        self.module.msgHandler(ThalesZMQMessage(SSDMessages.run()))
        sleep(10)

        log.info("STOP FIO tool")
        self.module.msgHandler(ThalesZMQMessage(SSDMessages.stop()))
        sleep(3)

        log.info("RUN again FIO tool")
        self.module.msgHandler(ThalesZMQMessage(SSDMessages.run()))
        sleep(10)

        log.info("STOP again FIO tool")
        self.module.msgHandler(ThalesZMQMessage(SSDMessages.stop()))
        sleep(3)

        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond
