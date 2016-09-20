import time
import unittest
from datetime import datetime

from rtc import Rtc
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.pb2.RTC_pb2 import *


# @cond doxygen_unittest

## RTC Messages
class RtcMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Real Time Clock"

    @staticmethod
    def getMenuItems():
        return [("RTC GetTime" , RtcMessages.message_RTC_GET),
                ("RTC SetTime" , RtcMessages.message_RTC_SET)]

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
        ConfigurableObject.setFilename("qual")
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

if __name__ == '__main__':
    unittest.main()

## @endcond
