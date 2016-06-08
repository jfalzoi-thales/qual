import unittest
import time

from qual.modules.rs485.rs485 import Rs485
from common.gpb.python.RS485_pb2 import RS485Request
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

## RS-485 Messages
class RS485Messages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "RS-485"

    @staticmethod
    def getMenuItems():
        return [("Report",  RS485Messages.report),
                ("Run",     RS485Messages.run),
                ("Stop",    RS485Messages.stop)]

    @staticmethod
    def report():
        message = RS485Request()
        message.requestType = RS485Request.REPORT
        return message

    @staticmethod
    def run():
        message = RS485Request()
        message.requestType = RS485Request.RUN
        return message

    @staticmethod
    def stop():
        message = RS485Request()
        message.requestType = RS485Request.STOP
        return message

## RS-485 Unit Test
class Test_RS485(unittest.TestCase):
    def test_basic(self):
        # Initialize logging
        log = Logger(name='Test RS485')
        log.info('Running test...')

        # RS485 Module Object
        self.module = Rs485()

        log.info("Send REPORT message before start running.")
        self.module.msgHandler(ThalesZMQMessage(RS485Messages.report()))
        time.sleep(3)

        log.info("Send RUN message.")
        self.module.msgHandler(ThalesZMQMessage(RS485Messages.run()))
        time.sleep(3)

        log.info("Send REPORT messages for 20 seconds.")
        for i in range(10):
            log.info("Sending REPORT message.")
            self.module.msgHandler(ThalesZMQMessage(RS485Messages.report()))
            time.sleep(2)

        log.info("Send STOP message.")
        self.module.msgHandler(ThalesZMQMessage(RS485Messages.stop()))
        time.sleep(3)

        log.info("Send REPORT message after stop.")
        self.module.msgHandler(ThalesZMQMessage(RS485Messages.report()))
        time.sleep(3)

        log.info("Send RUN message after stop.")
        self.module.msgHandler(ThalesZMQMessage(RS485Messages.run()))
        time.sleep(3)

        log.info("Send REPORT messages for 20 seconds.")
        for i in range(10):
            log.info("Sending REPORT message.")
            self.module.msgHandler(ThalesZMQMessage(RS485Messages.report()))
            time.sleep(2)

        log.info("Send STOP message.")
        self.module.msgHandler(ThalesZMQMessage(RS485Messages.stop()))
        time.sleep(3)

        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()
