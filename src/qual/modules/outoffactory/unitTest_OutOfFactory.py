import unittest
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.modules.outoffactory.outOfFactory import *
from qual.pb2.OOF_pb2 import *


# @cond doxygen_unittest

## OOF Messages
class OofMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Out Of Factory"

    @staticmethod
    def getMenuItems():
        return [("Send Erase SSD", OofMessages.message_SSDErase)]

    @staticmethod
    def message_SSDErase():
        message = SSDEraseRequest()
        return message

## Out Of Factory Unit Test
class Test_Oof(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the Oof test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Out Of Factory')
        cls.log.info('++++ Setup before OOF module unit tests ++++')
        # Create the module
        cls.module = Oof()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with OOF test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after Out Of Factory module unit tests ++++")
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
    def test_Oof(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: SSDErase Request message ****")

        oofResponse = module.msgHandler(ThalesZMQMessage(OofMessages.message_SSDErase()))
        # Asserts
        self.assertTrue(oofResponse.body.success)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond