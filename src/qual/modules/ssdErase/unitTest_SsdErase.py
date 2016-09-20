import unittest
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.modules.ssdErase.ssdErase import *
from qual.pb2.SSDErase_pb2 import *


# @cond doxygen_unittest

## SSDErase Messages
class SSDEraseMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "SSD Erase"

    @staticmethod
    def getMenuItems():
        return [("Send Erase SSD", SSDEraseMessages.message_SSDErase)]

    @staticmethod
    def message_SSDErase():
        message = SSDEraseRequest()
        message.erase = True
        return message

## SSDErase Unit Test
class Test_SSDErase(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the SSDErase test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='SSD Erase')
        cls.log.info('++++ Setup before SSDErase module unit tests ++++')
        # Create the module
        cls.module = SSDErase()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with SSDErase test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after SSDErase module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    #  This is run before each test case; we use it to make sure we
    #  start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")

    ## Valid Test case: Send a SSDErase Request
    #  Asserts:
    #    success == True
    def test_SSDErase(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: SSDErase Request message ****")

        SSDEraseResponse = module.msgHandler(ThalesZMQMessage(SSDEraseMessages.message_SSDErase()))
        # Asserts
        self.assertTrue(SSDEraseResponse.body.success)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond