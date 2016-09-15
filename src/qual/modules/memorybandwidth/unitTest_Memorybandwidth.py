import time
import unittest

from memorybandwidth import MemoryBandwidth
from qual.pb2.MemoryBandwidth_pb2 import MemoryBandwidthRequest, MemoryBandwidthResponse
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


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
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the Memory Bandwidth test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test Memory Bandwidth')
        cls.log.info('++++ Setup before Memory Bandwidth module unit tests ++++')
        # Create the module
        cls.module = MemoryBandwidth()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with Memory Bandwidth test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after Memory Bandwidth module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.stop()))

    ## Valid Test case: Send a START msg
    # Asserts:
    #       appState == RUNNING
    #       Memory Bandwidth == 0
    def test_Start(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: START message ****")
        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.run()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.RUNNING)
        self.assertEqual(response.body.memoryBandWidth, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a REPORT msg
    # Asserts:
    #       appState == STOPPED
    #       Memory Bandwidth == 0
    def test_Report(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: REPORT message ****")
        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.report()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.STOPPED)
        self.assertEqual(response.body.memoryBandWidth, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a STOP msg
    # Asserts:
    #       appState == STOPPED
    #       Memory Bandwidth == 0
    def test_Stop(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: STOP message ****")
        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.stop()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.STOPPED)
        self.assertEqual(response.body.memoryBandWidth, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a START, REPORT and STOP msgs
    # Asserts:
    #       appState == RUNNING
    #       Memory Bandwidth == 0
    #       ---------------------
    #       appState == RUNNING
    #       Memory Bandwidth > 0
    #       ---------------------
    #       appState == STOPPED
    #       Memory Bandwidth > 0
    #       ---------------------
    def test_StartReportStop(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: START, REPORT and STOP messages ****")

        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.run()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.RUNNING)
        self.assertEqual(response.body.memoryBandWidth, 0)

        # Allow pmbw tool run for a sec
        time.sleep(2)

        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.report()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.RUNNING)
        self.assertGreater(response.body.memoryBandWidth, 0)

        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.stop()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.STOPPED)
        self.assertGreater(response.body.memoryBandWidth, 0)

    ## Valid Test case: Send a START, START msgs
    # Asserts:
    #       appState == RUNNING
    #       Memory Bandwidth == 0
    #       ---------------------
    #       appState == RUNNING
    #       Memory Bandwidth == 0
    #       ---------------------
    def test_StartStart(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: START and START messages ****")

        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.run()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.RUNNING)
        self.assertEqual(response.body.memoryBandWidth, 0)

        # Allow pmbw tool run for a sec
        time.sleep(2)

        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.run()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.RUNNING)
        self.assertEqual(response.body.memoryBandWidth, 0)

    ## Valid Test case: Send a START, START and REPORT msgs
    # Asserts:
    #       appState == RUNNING
    #       Memory Bandwidth == 0
    #       ---------------------
    #       appState == RUNNING
    #       Memory Bandwidth == 0
    #       ---------------------
    #       appState == RUNNING
    #       Memory Bandwidth > 0
    #       ---------------------
    def test_StartStartReport(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: START, START and REPORT messages ****")

        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.run()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.RUNNING)
        self.assertEqual(response.body.memoryBandWidth, 0)

        # Allow pmbw tool run for a sec
        time.sleep(2)

        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.run()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.RUNNING)
        self.assertEqual(response.body.memoryBandWidth, 0)

        # Allow pmbw tool run for a sec
        time.sleep(2)

        response = module.msgHandler(ThalesZMQMessage(MemoryBandwidthMessages.report()))
        # Asserts
        self.assertEqual(response.name, "MemoryBandwidthResponse")
        self.assertEqual(response.body.state, MemoryBandwidthResponse.RUNNING)
        self.assertGreater(response.body.memoryBandWidth, 0)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
