import unittest
import time
from nms.guest.pb2.nms_guest_api_pb2 import *
from nms.guest.modules.configportstate.configPortState import PortStateConfig
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## Config Port States Messages
class ConfigPortStateMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Config Port State"

    @staticmethod
    def getMenuItems():
        return [("Send BLOCKING",   ConfigPortStateMessages.blocking),
                ("Send LISTENING",  ConfigPortStateMessages.listening),
                ("Send LLEARNING",  ConfigPortStateMessages.learning),
                ("Send FORWARDING", ConfigPortStateMessages.forwarding),
                ("Send DISABLED",   ConfigPortStateMessages.desabled)]

    @staticmethod
    def blocking():
        message = ConfigPortStateReq()
        portState = message.state.add()
        portState.namedPort = "internal.i350_1"
        portState.state = BLOCKING
        return message

    @staticmethod
    def listening():
        message = ConfigPortStateReq()
        portState = message.state.add()
        portState.namedPort = "internal.i350_1"
        portState.state = LISTENING
        return message

    @staticmethod
    def learning():
        message = ConfigPortStateReq()
        portState = message.state.add()
        portState.namedPort = "internal.i350_1"
        portState.state = LEARNING
        return message

    @staticmethod
    def forwarding():
        message = ConfigPortStateReq()
        portState = message.state.add()
        portState.namedPort = "internal.i350_1"
        portState.state = FORWARDING
        return message

    @staticmethod
    def disabled():
        message = ConfigPortStateReq()
        portState = message.state.add()
        portState.namedPort = "internal.i350_1"
        portState.state = DISABLED
        return message

## ConfigPortState Unit Test
class Test_ConfigPortState(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the Config Port State test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test Config Port State')
        cls.log.info('++++ Setup before Config Port State module unit tests ++++')
        # Create the module
        cls.module = PortStateConfig()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with Config Port State test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after Config Port State module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        msg = ConfigPortStateMessages.listening()
        zmqMsg = ThalesZMQMessage(msg)
        module.msgHandler(zmqMsg)

    ## Valid Test case:
    #
    def test_Block(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: BLOCKING message ****")
        response = module.msgHandler(ThalesZMQMessage(ConfigPortStateMessages.blocking()))
        # Asserts

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
