import unittest
from time import sleep

import arinc485
from qual.pb2.ARINC485_pb2 import ARINC485Request, ARINC485Response
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger import logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


# @cond doxygen_unittest

## ARINC485 Messages
class ARINC485Messages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "ARINC 485"

    @staticmethod
    def getMenuItems():
        return [("Report",  ARINC485Messages.report),
                ("Run",     ARINC485Messages.run),
                ("Stop",    ARINC485Messages.stop)]

    @staticmethod
    def report():
        message = ARINC485Request()
        message.requestType = ARINC485Request.REPORT
        return message

    @staticmethod
    def run():
        message = ARINC485Request()
        message.requestType = ARINC485Request.RUN
        return message

    @staticmethod
    def stop():
        message = ARINC485Request()
        message.requestType = ARINC485Request.STOP
        return message


## ARINC485 Unit Test
class Test_ARINC485(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the ARINC485 test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = logger.Logger(name='Test ARINC485')
        cls.log.info('++++ Setup before ARINC485 module unit tests ++++')
        #  Create the module
        if cls.module is None:
            cls.module = arinc485.ARINC485()

    ## Teardown when done with ARINC485 test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after ARINC485 module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    #  This is run before each test case; we use it to make sure we
    #  start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(ARINC485Messages.stop()))

    ## Valid Test case: Send a RUN, REPORT, STOP, and REPORT msgs
    # Map:
    #       RX    -> TX1, TX2, TX3, TX4
    #       RX not-> TX5
    #  Asserts:
    #       appState == RUNNING
    #       ---------------------
    #       appState == RUNNING
    #       ---------------------
    #       appState == STOPPED
    #       ---------------------
    #       appState == STOPPED
    #       ---------------------
    def test_RunReportStop(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN, REPORT and STOP messages ****")

        response = module.msgHandler(ThalesZMQMessage(ARINC485Messages.run()))
        self.assertEqual(response.name, "ARINC485Response")
        self.assertEqual(response.body.state, ARINC485Response.RUNNING)

        for stats in response.body.statistics:
            self.assertEqual(stats.missed, 0)
            self.assertEqual(stats.received, 0)

        log.info("==== Wait 5 seconds to accumulate statistics ====")
        sleep(5)

        response = module.msgHandler(ThalesZMQMessage(ARINC485Messages.report()))
        self.assertEqual(response.name, "ARINC485Response")
        self.assertEqual(response.body.state, ARINC485Response.RUNNING)

        for stats in response.body.statistics:
            if stats.channel in ["Slave1", "Slave2", "Slave3", "Slave4"]:
                self.assertEqual(stats.missed, 0)
                self.assertGreater(stats.received, 0)

            if stats.channel in ["Slave5"]:
                self.assertGreater(stats.missed, 0)
                self.assertEqual(stats.received, 0)

        response = module.msgHandler(ThalesZMQMessage(ARINC485Messages.stop()))
        self.assertEqual(response.name, "ARINC485Response")
        self.assertEqual(response.body.state, ARINC485Response.STOPPED)

        for stats in response.body.statistics:
            if stats.channel in ["Slave1", "Slave2", "Slave3", "Slave4"]:
                self.assertEqual(stats.missed, 0)
                self.assertGreater(stats.received, 0)

            if stats.channel in ["Slave5"]:
                self.assertGreater(stats.missed, 0)
                self.assertEqual(stats.received, 0)

        response = module.msgHandler(ThalesZMQMessage(ARINC485Messages.report()))
        self.assertEqual(response.name, "ARINC485Response")
        self.assertEqual(response.body.state, ARINC485Response.STOPPED)

        for stats in response.body.statistics:
            self.assertEqual(stats.missed, 0)
            self.assertEqual(stats.received, 0)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond