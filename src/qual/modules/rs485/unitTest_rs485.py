import time
import unittest

from qual.pb2.RS485_pb2 import RS485Request, RS485Response
from rs485 import Rs485
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


# @cond doxygen_unittest

## RS-485 Messages
class RS485Messages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "RS-485"

    @staticmethod
    def getMenuItems():
        return [("Report",  RS485Messages.report),
                ("Run",     RS485Messages.run),
                ("Stop",    RS485Messages.stop)]

    @staticmethod
    def report():
        message = RS485Request()
        message.requestType = RS485Request.REPORT
        return message

    @staticmethod
    def run():
        message = RS485Request()
        message.requestType = RS485Request.RUN
        return message

    @staticmethod
    def stop():
        message = RS485Request()
        message.requestType = RS485Request.STOP
        return message

## RS485 Unit Test
class Test_RS485(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the RS-485 test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test RS-485')
        cls.log.info('++++ Setup before RS-485 module unit tests ++++')
        # Create the module
        cls.module = Rs485()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with RS-485 test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after RS-485 module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(RS485Messages.stop()))

    ## Valid Test case: Send a RUN msg
    # Asserts:
    #       appState == RUNNING
    #       xmtCount == 0
    #       matches == 0
    #       mismatches == 0
    def test_Run(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN message ****")
        response = module.msgHandler(ThalesZMQMessage(RS485Messages.run()))
        # Asserts
        self.assertEqual(response.name, "RS485Response")
        self.assertEqual(response.body.state, RS485Response.RUNNING)
        self.assertEqual(response.body.xmtCount, 0)
        self.assertEqual(response.body.matches, 0)
        self.assertEqual(response.body.mismatches, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a REPORT msg
    # Asserts:
    #       appState == STOPPED
    #       xmtCount == 0
    #       matches == 0
    #       mismatches == 0
    def test_Report(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: REPORT message ****")
        response = module.msgHandler(ThalesZMQMessage(RS485Messages.report()))
        # Asserts
        self.assertEqual(response.name, "RS485Response")
        self.assertEqual(response.body.state, RS485Response.STOPPED)
        self.assertEqual(response.body.xmtCount, 0)
        self.assertEqual(response.body.matches, 0)
        self.assertEqual(response.body.mismatches, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a STOP msg
    # Asserts:
    #       appState == STOPPED
    #       xmtCount == 0
    #       matches == 0
    #       mismatches == 0
    def test_Stop(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: STOP message ****")
        response = module.msgHandler(ThalesZMQMessage(RS485Messages.stop()))
        # Asserts
        self.assertEqual(response.name, "RS485Response")
        self.assertEqual(response.body.state, RS485Response.STOPPED)
        self.assertEqual(response.body.xmtCount, 0)
        self.assertEqual(response.body.matches, 0)
        self.assertEqual(response.body.mismatches, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RUN, REPORT and STOP msgs
    # Asserts:
    #       appState == RUNNING
    #       xmtCount == 0
    #       matches == 0
    #       mismatches == 0
    #       ---------------------
    #       appState == RUNNING
    #       xmtCount > 0
    #       matches > 0
    #       mismatches >= 0
    #       ---------------------
    #       appState == STOPPED
    #       xmtCount > 0
    #       matches > 0
    #       mismatches >= 0
    #       ---------------------
    def test_RunReportStop(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN, REPORT and STOP messages ****")

        response = module.msgHandler(ThalesZMQMessage(RS485Messages.run()))
        # Asserts
        self.assertEqual(response.name, "RS485Response")
        self.assertEqual(response.body.state, RS485Response.RUNNING)
        self.assertEqual(response.body.xmtCount, 0)
        self.assertEqual(response.body.matches, 0)
        self.assertEqual(response.body.mismatches, 0)

        # Allow RS-485 send some data
        time.sleep(2)

        response = module.msgHandler(ThalesZMQMessage(RS485Messages.report()))
        # Asserts
        self.assertEqual(response.name, "RS485Response")
        self.assertEqual(response.body.state, RS485Response.RUNNING)
        self.assertGreater(response.body.xmtCount, 0)
        self.assertGreater(response.body.matches, 0)
        self.assertGreaterEqual(response.body.mismatches, 0)

        response = module.msgHandler(ThalesZMQMessage(RS485Messages.stop()))
        # Asserts
        self.assertEqual(response.name, "RS485Response")
        self.assertEqual(response.body.state, RS485Response.STOPPED)
        self.assertGreater(response.body.xmtCount, 0)
        self.assertGreater(response.body.matches, 0)
        self.assertGreaterEqual(response.body.mismatches, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a START, START and REPORT msgs
    # Asserts:
    #       appState == RUNNING
    #       xmtCount == 0
    #       matches == 0
    #       mismatches == 0
    #       ---------------------
    #       appState == RUNNING
    #       xmtCount == 0
    #       matches == 0
    #       mismatches == 0
    #       ---------------------
    #       appState == RUNNING
    #       xmtCount > 0
    #       matches > 0
    #       mismatches >= 0
    def test_StartStartReport(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: START, START and REPORT messages ****")

        response = module.msgHandler(ThalesZMQMessage(RS485Messages.run()))
        # Asserts
        self.assertEqual(response.name, "RS485Response")
        self.assertEqual(response.body.state, RS485Response.RUNNING)
        self.assertEqual(response.body.xmtCount, 0)
        self.assertEqual(response.body.matches, 0)
        self.assertEqual(response.body.mismatches, 0)

        # Allow RS-485 send some data
        time.sleep(2)

        response = module.msgHandler(ThalesZMQMessage(RS485Messages.run()))
        # Asserts
        self.assertEqual(response.name, "RS485Response")
        self.assertEqual(response.body.state, RS485Response.RUNNING)
        self.assertEqual(response.body.xmtCount, 0)
        self.assertEqual(response.body.matches, 0)
        self.assertEqual(response.body.mismatches, 0)

        # Allow RS-485 send some data
        time.sleep(2)

        response = module.msgHandler(ThalesZMQMessage(RS485Messages.report()))
        # Asserts
        self.assertEqual(response.name, "RS485Response")
        self.assertEqual(response.body.state, RS485Response.RUNNING)
        self.assertGreater(response.body.xmtCount, 0)
        self.assertGreater(response.body.matches, 0)
        self.assertGreaterEqual(response.body.mismatches, 0)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
