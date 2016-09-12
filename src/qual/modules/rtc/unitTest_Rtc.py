import time
import unittest
from datetime import datetime
from common.pb2.rtc_driver_pb2 import *
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.modules.rtc.rtc import *
from qual.pb2.RTC_pb2 import *


# @cond doxygen_unittest

## RTC Messages
class RtcMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Real Time Clock"

    @staticmethod
    def getMenuItems():
        return [("GetTime", RtcMessages.getTime),
                ("SetTime", RtcMessages.setTime),
                ("RTC_GET", RtcMessages.message_RTC_GET),
                ("RTC_SET", RtcMessages.message_RTC_SET)]

    @staticmethod
    def message_RTC_GET():
        message = RTCRequest()
        message.requestType = RTCRequest.RTC_GET
        return message

    @staticmethod
    def message_RTC_SET():
        message = RTCRequest()
        message.requestType = RTCRequest.RTC_SET
        message.timeString = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
        return message

    @staticmethod
    def message_SYSTEM_TO_RTC():
        message = RTCRequest()
        message.requestType = RTCRequest.SYSTEM_TO_RTC
        return message

    @staticmethod
    def message_RTC_TO_SYSTEM():
        message = RTCRequest()
        message.requestType = RTCRequest.RTC_TO_SYSTEM
        return message

    @staticmethod
    def message_RTC_SYSTEM_SET():
        message = RTCRequest()
        message.requestType = RTCRequest.RTC_SYSTEM_SET
        message.timeString = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
        return message

## RTC Unit Test
class Test_Rtc(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the Rtc test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test Real Time Clock')
        cls.log.info('++++ Setup before RTC module unit tests ++++')
        # Create the module
        cls.module = Rtc()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with RTC test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after Real Time Clock module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    #  This is run before each test case; we use it to make sure we
    #  start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")

    ## Valid Test case: Send a RTC Request RTC_GET msg
    #  Asserts:
    #    success == True
    #    timeString is an unicode str
    def test_Message_RTC_GET(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RTC Request message RTC_GET ****")
        response = module.msgHandler(ThalesZMQMessage(RtcMessages.message_RTC_GET()))
        # Asserts
        self.assertTrue(response.body.success)
        self.assertTrue(isinstance(response.body.timeString, unicode))
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RTC Request RTC_SET msg
    #  Asserts:
    #    success == True
    #    timeString is an unicode str
    def test_Message_RTC_SET(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RTC Request message RTC_SET ****")
        response = module.msgHandler(ThalesZMQMessage(RtcMessages.message_RTC_SET()))
        # Asserts
        self.assertTrue(response.body.success)
        self.assertTrue(isinstance(response.body.timeString, unicode))
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RTC Request SYSTEM_TO_RTC msg
    #  Asserts:
    #    success == True
    #    timeString is an unicode str
    def test_Message_SYSTEM_TO_RTC(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RTC Request message SYSTEM_TO_RTC ****")
        response = module.msgHandler(ThalesZMQMessage(RtcMessages.message_SYSTEM_TO_RTC()))
        # Asserts
        self.assertTrue(response.body.success)
        self.assertTrue(isinstance(response.body.timeString, unicode))
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RTC Request RTC_TO_SYSTEM msg
    #  Asserts:
    #    success == True
    #    timeString is an unicode str
    def test_Message_RTC_TO_SYSTEM(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RTC Request message RTC_TO_SYSTEM ****")
        response = module.msgHandler(ThalesZMQMessage(RtcMessages.message_RTC_TO_SYSTEM()))
        # Asserts
        self.assertTrue(response.body.success)
        self.assertTrue(isinstance(response.body.timeString, unicode))
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RTC Request RTC_SYSTEM_SET msg
    #  Asserts:
    #    success == True
    #    timeString is an unicode str
    def test_Message_RTC_SYSTEM_SET(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RTC Request message RTC_TO_SYSTEM ****")
        response = module.msgHandler(ThalesZMQMessage(RtcMessages.message_RTC_SYSTEM_SET()))
        # Asserts
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")
        self.assertTrue(isinstance(response.body.timeString, unicode))


if __name__ == '__main__':
    unittest.main()

## @endcond