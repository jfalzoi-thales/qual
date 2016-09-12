import time
import unittest
from datetime import datetime
from common.pb2.rtc_driver_pb2 import *
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.modules.rtc.rtc import *


# @cond doxygen_unittest

## RTC Messages
class RtcMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Real Time Clock"

    @staticmethod
    def getMenuItems():
        return [("GetTime", RtcMessages.getTime),
                ("SetTime", RtcMessages.setTime)]

    @staticmethod
    def getTime():
        message = GetTime()
        return message

    @staticmethod
    def setTime():
        message = SetTime()
        message.datetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
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
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")

    ## Valid Test case: Send a GetTime msg
    # Asserts:
    #   error == SUCCESS
    #   datetime is an unicode str
    def test_GetTime(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: GetTime message ****")
        response = module.msgHandler(ThalesZMQMessage(RtcMessages.getTime()))
        # Asserts
        self.assertEqual(response.body.error, SUCCESS)
        self.assertTrue(isinstance(response.body.datetime, unicode))
        log.info("==== Test complete ====")


    ## Valid Test case: Send a SetTime msg
    # Asserts:
    #   error == SUCCESS
    def test_SetTime(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: SetTime message ****")
        response = module.msgHandler(ThalesZMQMessage(RtcMessages.setTime()))
        getResp = TimeResponse()
        getResp.ParseFromString(response.serializedBody)
        # Asserts
        self.assertEqual(response.body.error, SUCCESS)
        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
