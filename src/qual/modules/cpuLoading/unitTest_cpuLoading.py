import time
import unittest

import cpuLoading
from qual.pb2.CPULoading_pb2 import CPULoadingRequest, CPULoadingResponse
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


#  @cond doxygen_unittest

## CPULoading Messages
class CPULoadingMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "CPU Loading"

    @staticmethod
    def getMenuItems():
        return [("Report",                   CPULoadingMessages.report),
                ("Run - default load (80%)", CPULoadingMessages.runDefault),
                ("Run - 50% load",           CPULoadingMessages.run50),
                ("Stop",                     CPULoadingMessages.stop)]

    @staticmethod
    def report():
        message = CPULoadingRequest()
        message.requestType = CPULoadingRequest.REPORT
        return message

    @staticmethod
    def runDefault():
        message = CPULoadingRequest()
        message.requestType = CPULoadingRequest.RUN
        return message

    @staticmethod
    def run50():
        message = CPULoadingRequest()
        message.requestType = CPULoadingRequest.RUN
        message.level = 50
        return message

    @staticmethod
    def stop():
        message = CPULoadingRequest()
        message.requestType = CPULoadingRequest.STOP
        return message

## CPULoading Unit Test
class Test_CPULoading(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the CPULoading test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test CPULoading')
        cls.log.info('++++ Setup before CPULoading module unit tests ++++')
        # Create the module
        cls.module = cpuLoading.CPULoading()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with CPULoading test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after CPULoading module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(CPULoadingMessages.stop()))

    ## Valid Test case: Send a REPORT msg
    # Asserts:
    #       appState == STOPPED
    #       totalUtilization == 0
    #       --------------------
    def test_Report(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: REPORT message ****")

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.report()))

        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.STOPPED)
        self.assertGreaterEqual(response.body.totalUtilization, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a STOP msg
    # Asserts:
    #       appState == STOPPED
    #       totalUtilization == 0
    #       --------------------
    def test_Report(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: STOP message ****")

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.stop()))

        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.STOPPED)
        self.assertGreaterEqual(response.body.totalUtilization, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RUN(default), REPORT and STOP msgs
    # Asserts:
    #       appState == RUNNING
    #       totalUtilization == 0
    #       --------------------
    #       appState == RUNNING
    #       totalUtilization > 0
    def test_RunDef(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: REPORT message ****")

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.runDefault()))

        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.RUNNING)
        self.assertGreater(response.body.totalUtilization, 0)

        # Allow lookbusy run for a while
        time.sleep(1)

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.report()))

        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.RUNNING)
        self.assertGreater(response.body.totalUtilization, 0)
        log.info("==== Test complete ====")

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.stop()))

        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.STOPPED)
        self.assertGreater(response.body.totalUtilization, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RUN(50%), REPORT and STOP msgs
    # Asserts:
    #       appState == RUNNING
    #       totalUtilization == 0
    #       --------------------
    #       appState == RUNNING
    #       totalUtilization > 0
    #       --------------------
    #       appState == STOPPED
    #       totalUtilization > 0
    #       --------------------
    def test_Run50(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: REPORT message ****")

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.runDefault()))

        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.RUNNING)
        self.assertGreaterEqual(response.body.totalUtilization, 0)

        # Allow lookbusy run for a while
        time.sleep(1)

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.report()))

        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.RUNNING)
        self.assertGreater(response.body.totalUtilization, 0)
        log.info("==== Test complete ====")

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.stop()))

        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.STOPPED)
        self.assertGreater(response.body.totalUtilization, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RUN, STOP, RUN and Stop msgs
    # Asserts:
    #       appState == RUNNING
    #       totalUtilization == 0
    #       --------------------
    #       appState == STOPPED
    #       totalUtilization > 0
    #       --------------------
    #       appState == RUNNING
    #       totalUtilization == 0
    #       --------------------
    #       appState == STOPPED
    #       totalUtilization > 0
    #       --------------------
    def test_RunStopRunStop(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN, STOP, RUN AND STOP message ****")

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.runDefault()))
        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.RUNNING)
        self.assertGreater(response.body.totalUtilization, 0)

        # Allow lookbusy run for a while
        time.sleep(1)

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.stop()))
        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.STOPPED)
        self.assertGreater(response.body.totalUtilization, 0)

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.runDefault()))
        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.RUNNING)
        self.assertGreater(response.body.totalUtilization, 0)

        # Allow lookbusy run for a while
        time.sleep(1)

        response = module.msgHandler(ThalesZMQMessage(CPULoadingMessages.stop()))
        # Asserts
        self.assertEqual(response.name, "CPULoadingResponse")
        self.assertEqual(response.body.state, CPULoadingResponse.STOPPED)
        self.assertGreater(response.body.totalUtilization, 0)
        log.info("==== Test complete ====")

    ## Invalid Test case: Send a RUN(>100%) msgs
    # Asserts:
    #       appState == STOPPED
    #       --------------------
    def test_Run_Invalid1(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Invalid loading percent ****")

        # Create the wrong request msg
        message = CPULoadingRequest()
        message.requestType = CPULoadingRequest.RUN
        message.level = 120

        response = module.msgHandler(ThalesZMQMessage(message))
        self.assertEqual(response.body.state, CPULoadingResponse.STOPPED)
        log.info("==== Test complete ====")

    ## Invalid Test case: Send a RUN(<0%) msgs
    # Asserts:
    #       appState == STOPPED
    #       --------------------
    def test_Run_Invalid2(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Invalid loading percent ****")

        # Create the wrong request msg
        message = CPULoadingRequest()
        message.requestType = CPULoadingRequest.RUN
        message.level = -80

        response = module.msgHandler(ThalesZMQMessage(message))
        self.assertEqual(response.body.state, CPULoadingResponse.STOPPED)
        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond