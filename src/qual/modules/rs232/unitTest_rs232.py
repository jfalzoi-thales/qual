import unittest
import time
from qual.modules.rs232.rs232 import Rs232
from common.gpb.python.RS232_pb2 import RS232Request
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## RS-232 Messages
class RS232Messages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "RS-232"

    @staticmethod
    def getMenuItems():
        return [("Report",  RS232Messages.report),
                ("Run",     RS232Messages.run),
                ("Stop",    RS232Messages.stop)]

    @staticmethod
    def report():
        message = RS232Request()
        message.requestType = RS232Request.REPORT
        return message

    @staticmethod
    def run():
        message = RS232Request()
        message.requestType = RS232Request.RUN
        return message

    @staticmethod
    def stop():
        message = RS232Request()
        message.requestType = RS232Request.STOP
        return message

## RS-232 Unit Test
class Test_Rs232(unittest.TestCase):
    def test_rs232(self):
        # Initialize logging
        log = Logger(name='Test RS-232')
        log.info('Running test...')

        # RS232 Module Object
        self.module =  Rs232(config=Rs232.getConfigurations()[0])

        log.info("Send REPORT message before start running.")
        self.module.msgHandler(ThalesZMQMessage(RS232Messages.report()))
        time.sleep(3)

        log.info("Send RUN message.")
        self.module.msgHandler(ThalesZMQMessage(RS232Messages.run()))
        time.sleep(3)

        log.info("Send REPORT messages for 20 seconds.")
        for i in range(10):
            log.info("Sending REPORT message.")
            self.module.msgHandler(ThalesZMQMessage(RS232Messages.report()))
            time.sleep(2)

        log.info("Send STOP message.")
        self.module.msgHandler(ThalesZMQMessage(RS232Messages.stop()))
        time.sleep(3)

        log.info("Send REPORT message after stop.")
        self.module.msgHandler(ThalesZMQMessage(RS232Messages.report()))
        time.sleep(3)

        log.info("Send RUN message after stop.")
        self.module.msgHandler(ThalesZMQMessage(RS232Messages.run()))
        time.sleep(3)

        log.info("Send REPORT messages for 20 seconds.")
        for i in range(10):
            log.info("Sending REPORT message.")
            self.module.msgHandler(ThalesZMQMessage(RS232Messages.report()))
            time.sleep(2)

        log.info("Send STOP message.")
        self.module.msgHandler(ThalesZMQMessage(RS232Messages.stop()))
        time.sleep(3)

        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond
