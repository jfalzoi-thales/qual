import unittest
import os

from time import sleep
from common.gpb.python.SSD_pb2 import SSDRequest, SSDResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages
from qual.modules.ssd.ssd import SSD
from qual.modules.ssd.ssd_Exception import SSDModuleException

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
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the SSD test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test SSD')
        cls.log.info('++++ Setup before SSD module unit tests ++++')
        # Create the module
        cls.module = SSD()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with SSD test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after SSD module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(SSDMessages.stop()))

    ## Valid Test case: Send a RUN and STOP msgs
    # Asserts:
    #       appState == RUNNING
    #       --------------------
    #       appState == STOPPED
    #       --------------------
    def test_RunStop(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN and Stop messages ****")

        response = module.msgHandler(ThalesZMQMessage(SSDMessages.run()))
        # Asserts
        self.assertEqual(response.name, "SSDResponse")

        self.assertEqual(response.body.state, SSDResponse.RUNNING)

        response = module.msgHandler(ThalesZMQMessage(SSDMessages.stop()))
        # Asserts
        self.assertEqual(response.name, "SSDResponse")
        self.assertEqual(response.body.state, SSDResponse.STOPPED)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RUN msg
    # Asserts:
    #       appState == RUNNING
    #       --------------------
    def test_Run(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Test case: RUN message ****")
        response = module.msgHandler(ThalesZMQMessage(SSDMessages.run()))
        # Asserts
        self.assertEqual(response.name, "SSDResponse")
        self.assertEqual(response.body.state, SSDResponse.RUNNING)
        log.info("==== Test complete ====")


    ## Valid Test case: Send a STOP msg
    # Asserts:
    #       appState == STOPPED
    #       --------------------
    def test_Stop(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Test case: STOP messages ****")
        response = module.msgHandler(ThalesZMQMessage(SSDMessages.stop()))
        # Asserts
        self.assertEqual(response.name, "SSDResponse")
        self.assertEqual(response.body.state, SSDResponse.STOPPED)
        log.info("==== Test complete ====")


if __name__ == '__main__':
    # Save the current working directory
    path = os.getcwd()
    # Move to src in order to run the file system scripts
    os.chdir('../../..')
    # Run the tests
    unittest.main()
    # Move back to the original directory
    os.chdir(path)

## @endcond
