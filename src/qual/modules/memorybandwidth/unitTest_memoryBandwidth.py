import unittest
import time
from qual.modules.memorybandwidth.memorybandwidth import MemoryBandwidth
from common.gpb.python.MemoryBandwidth_pb2 import MemoryBandwidthRequest
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## MemoryBandwidth Messages
class MemoryBandwidthMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Memory Bandwidth"

    @staticmethod
    def getMenuItems():
        return [("Report",  MemoryBandwidthMessages.report),
                ("Run",     MemoryBandwidthMessages.run),
                ("Stop",    MemoryBandwidthMessages.stop)]

    @staticmethod
    def report():
        message = MemoryBandwidthRequest()
        message.requestType = MemoryBandwidthRequest.REPORT
        return message

    @staticmethod
    def run():
        message = MemoryBandwidthRequest()
        message.requestType = MemoryBandwidthRequest.RUN
        return message

    @staticmethod
    def stop():
        message = MemoryBandwidthRequest()
        message.requestType = MemoryBandwidthRequest.STOP
        return message

## Memory Bandwidth Unit Test
class Test_MemoryBandwidth(unittest.TestCase):
    def test_membw(self):
        # Initialize logging
        log = Logger(name='Test Memory Bandwidth')
        log.info('Running test...')

        # MemoryBandwidth Module Object
        self.module = MemoryBandwidth(config=MemoryBandwidth.getConfigurations()[0])

        log.info("Send REPORT message before start running.")
        self.module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.report()))
        time.sleep(3)

        log.info("Send RUN message.")
        self.module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.run()))
        time.sleep(3)

        log.info("Send REPORT messages for 20 seconds.")
        for i in range(10):
            log.info("Sending REPORT message.")
            self.module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.report()))
            time.sleep(2)

        log.info("Send STOP message.")
        self.module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.stop()))
        time.sleep(3)

        log.info("Send REPORT message after stop.")
        self.module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.report()))
        time.sleep(3)

        log.info("Send RUN message after stop.")
        self.module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.run()))
        time.sleep(3)

        log.info("Send REPORT messages for 20 seconds.")
        for i in range(10):
            log.info("Sending REPORT message.")
            self.module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.report()))
            time.sleep(2)

        log.info("Send STOP message.")
        self.module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.stop()))
        time.sleep(3)

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond
