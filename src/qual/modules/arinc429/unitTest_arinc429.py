import unittest
from time import sleep

import arinc429
from qual.pb2.ARINC429_pb2 import ARINC429Request, ARINC429Response
from tklabs_utils.logger import logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


# @cond doxygen_unittest

## ARINC429 Messages
class ARINC429Messages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "ARINC 429"

    @staticmethod
    def getMenuItems():
        return [("Report for input 1",             ARINC429Messages.reportIn1),
                ("Report for input 3",             ARINC429Messages.reportIn3),
                ("Report for all inputs",          ARINC429Messages.reportAll),
                ("Connect input 1 to output 1",    ARINC429Messages.connectIn1Out1),
                ("Connect input 3 to output 1",    ARINC429Messages.connectIn3Out1),
                ("Connect input 3 to output 2",    ARINC429Messages.connectIn3Out2),
                ("Connect all inputs to output 3", ARINC429Messages.connectInAllOut3),
                ("Disconnect input 1",             ARINC429Messages.disconnectIn1),
                ("Disconnect input 3",             ARINC429Messages.disconnectIn3),
                ("Disconnect all inputs",          ARINC429Messages.disconnectAll)]

    @staticmethod
    def reportIn1():
        message = ARINC429Request()
        message.requestType = ARINC429Request.REPORT
        message.sink = "ARINC_429_RX1"
        return message

    @staticmethod
    def reportIn3():
        message = ARINC429Request()
        message.requestType = ARINC429Request.REPORT
        message.sink = "ARINC_429_RX3"
        return message

    @staticmethod
    def reportAll():
        message = ARINC429Request()
        message.requestType = ARINC429Request.REPORT
        message.sink = "ALL"
        return message

    @staticmethod
    def connectIn1Out1():
        message = ARINC429Request()
        message.requestType = ARINC429Request.CONNECT
        message.sink = "ARINC_429_RX1"
        message.source = "ARINC_429_TX1"
        return message

    @staticmethod
    def connectIn3Out1():
        message = ARINC429Request()
        message.requestType = ARINC429Request.CONNECT
        message.sink = "ARINC_429_RX3"
        message.source = "ARINC_429_TX1"
        return message

    @staticmethod
    def connectIn3Out2():
        message = ARINC429Request()
        message.requestType = ARINC429Request.CONNECT
        message.sink = "ARINC_429_RX3"
        message.source = "ARINC_429_TX2"
        return message

    @staticmethod
    def connectInAllOut3():
        message = ARINC429Request()
        message.requestType = ARINC429Request.CONNECT
        message.sink = "ALL"
        message.source = "ARINC_429_TX3"
        return message

    @staticmethod
    def disconnectIn1():
        message = ARINC429Request()
        message.requestType = ARINC429Request.DISCONNECT
        message.sink = "ARINC_429_RX1"
        return message

    @staticmethod
    def disconnectIn3():
        message = ARINC429Request()
        message.requestType = ARINC429Request.DISCONNECT
        message.sink = "ARINC_429_RX3"
        return message

    @staticmethod
    def disconnectAll():
        message = ARINC429Request()
        message.requestType = ARINC429Request.DISCONNECT
        message.sink = "ALL"
        return message

    @staticmethod
    def connectInBogus():
        message = ARINC429Request()
        message.requestType = ARINC429Request.CONNECT
        message.sink = "ARINC_429_BOGUS"
        message.source = "ARINC_429_TX2"
        return message

    @staticmethod
    def connectOutBogus():
        message = ARINC429Request()
        message.requestType = ARINC429Request.CONNECT
        message.sink = "ARINC_429_RX2"
        message.source = "ARINC_429_BOGUS"
        return message

    ## Constructor (not used)
    #  @param     self
    def __init__(self):
        super(ARINC429Messages, self).__init__()

## ARINC429 Unit Test
class Test_ARINC429(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the ARINC429 test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = logger.Logger(name='Test ARINC429')
        cls.log.info('++++ Setup before ARINC429 module unit tests ++++')
        # Create the module
        cls.module = arinc429.ARINC429()
        # Uncomment this if you don't want to see module debug messages
        #cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with ARINC429 test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after ARINC429 module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(ARINC429Messages.disconnectAll()))

    ## Test case: Try to connect an invalid input channel
    # Should return an empty ARINC429Response
    def test_invalidInput(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Invalid input channel specified ****")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectInBogus()))
        # Invalid input channel will return an empty ARINC429Response
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 0)
        log.info("==== Test complete ====")

    # Test case: Try to connect an invalid output channel
    # Should return an empty ARINC429Response
    def test_invalidOutput(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Invalid output channel specified ****")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectOutBogus()))
        # Invalid output channel will return an empty ARINC429Response
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 0)
        log.info("==== Test complete ====")

    ## Test case: Try to reconnect a connected input channel
    # Should return a ARINC429Response showing channel still connected to original output
    def test_reconnect(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Try to reconnect a connected input channel ****")
        log.info("==== Report before connecting ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportIn3()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.DISCONNECTED)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX3")
        self.assertEqual(response.body.status[0].source, "")

        log.info("==== Connect input ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectIn3Out1()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.CONNECTED)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX3")
        self.assertEqual(response.body.status[0].source, "ARINC_429_TX1")

        log.info("==== Try to connect input to different output ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectIn3Out2()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.CONNECTED)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX3")
        self.assertEqual(response.body.status[0].source, "ARINC_429_TX1")
        log.info("==== Test complete ====")

    ## Test case: Connect a linked input/output pair
    # This test case will connect a "linked" pair, wait 1 second, then
    # verify that the report indicates 4-5 matches and 0 mismatches.
    # It also verifies that the report is cleared when read back
    # after a disconnect.
    def test_linkedPair(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Connect a linked input/output pair ****")
        log.info("==== Report before connecting ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportIn1()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.DISCONNECTED)
        self.assertEqual(response.body.status[0].xmtCount, 0)
        self.assertEqual(response.body.status[0].rcvCount, 0)
        self.assertEqual(response.body.status[0].errorCount, 0)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX1")
        self.assertEqual(response.body.status[0].source, "")

        log.info("==== Connect linked pair ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectIn1Out1()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.CONNECTED)
        self.assertGreaterEqual(response.body.status[0].xmtCount, 0)
        self.assertGreaterEqual(response.body.status[0].xmtCount, response.body.status[0].rcvCount)
        self.assertGreaterEqual(response.body.status[0].errorCount, 0)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX1")
        self.assertEqual(response.body.status[0].source, "ARINC_429_TX1")

        log.info("==== Wait 5 seconds to accumulate statistics ====")
        sleep(5)

        log.info("==== Get report after 1 second ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportIn1()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.CONNECTED)
        self.assertGreaterEqual(response.body.status[0].xmtCount, 0)
        self.assertGreaterEqual(response.body.status[0].xmtCount, response.body.status[0].rcvCount)
        self.assertGreaterEqual(response.body.status[0].errorCount, 0)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX1")
        self.assertEqual(response.body.status[0].source, "ARINC_429_TX1")

        log.info("==== Disconnect connected pair ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.disconnectIn1()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.DISCONNECTED)
        self.assertGreater(response.body.status[0].xmtCount, 0)
        self.assertGreaterEqual(response.body.status[0].xmtCount, response.body.status[0].rcvCount)
        self.assertGreaterEqual(response.body.status[0].errorCount, 0)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX1")
        self.assertEqual(response.body.status[0].source, "ARINC_429_TX1")

        log.info("==== Report after disconnect ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportIn1()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.DISCONNECTED)
        self.assertEqual(response.body.status[0].xmtCount, 0)
        self.assertEqual(response.body.status[0].rcvCount, 0)
        self.assertEqual(response.body.status[0].errorCount, 0)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX1")
        self.assertEqual(response.body.status[0].source, "")
        log.info("==== Test complete ====")

    ## Test case: Connect an unlinked input/output pair
    # This test case will connect an "unlinked" pair, wait 1 second, then
    # verify that the report indicates 2-3 matches and 2-3 mismatches.
    def test_unlinkedPair(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Connect an unlinked input/output pair ****")
        log.info("==== Report before connecting ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportIn1()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.DISCONNECTED)
        self.assertEqual(response.body.status[0].xmtCount, 0)
        self.assertEqual(response.body.status[0].rcvCount, 0)
        self.assertEqual(response.body.status[0].errorCount, 0)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX1")
        self.assertEqual(response.body.status[0].source, "")

        log.info("==== Connect unlinked pair ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectIn3Out1()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.CONNECTED)
        self.assertGreaterEqual(response.body.status[0].xmtCount, 0)
        self.assertEqual(response.body.status[0].rcvCount, 0)
        self.assertEqual(response.body.status[0].errorCount, response.body.status[0].xmtCount)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX3")
        self.assertEqual(response.body.status[0].source, "ARINC_429_TX1")

        log.info("==== Wait 5 seconds to accumulate statistics ====")
        sleep(5)

        log.info("==== Disconnect connected pair and check results ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.disconnectIn3()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, ARINC429Response.DISCONNECTED)
        self.assertGreater(response.body.status[0].xmtCount, 0)
        self.assertEqual(response.body.status[0].rcvCount, 0)
        self.assertGreaterEqual(response.body.status[0].xmtCount, response.body.status[0].errorCount)
        self.assertEqual(response.body.status[0].sink, "ARINC_429_RX3")
        self.assertEqual(response.body.status[0].source, "ARINC_429_TX1")
        log.info("==== Test complete ====")

    ## Test case: Use of the "ALL" parameter
    # Tests CONNECT, DISCONNECT, and REPORT messages with the input
    # channel specified as "ALL" perform the correct actions.
    def test_allparam(self):
        log = self.__class__.log
        module = self.__class__.module

        numInputs = len(module.inputChans)

        log.info("**** Test case: Test use of the \"ALL\" parameter ****")
        log.info("==== Report on all inputs before connect ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportAll()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), numInputs)
        for ARINC429Stat in response.body.status:
            # All channels should be disconnected
            self.assertEqual(ARINC429Stat.conState, ARINC429Response.DISCONNECTED)
            self.assertEqual(ARINC429Stat.source, "")

        log.info("==== Connect all inputs ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectInAllOut3()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), numInputs)
        for ARINC429Stat in response.body.status:
            # All channels should be connected to output 3
            self.assertEqual(ARINC429Stat.conState, ARINC429Response.CONNECTED)
            self.assertEqual(ARINC429Stat.source, "ARINC_429_TX3")

        log.info("==== Report on all inputs after connect ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportAll()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), numInputs)
        for ARINC429Stat in response.body.status:
            # All channels should still be connected to output 3
            self.assertEqual(ARINC429Stat.conState, ARINC429Response.CONNECTED)
            self.assertEqual(ARINC429Stat.source, "ARINC_429_TX3")

        log.info("==== Wait 5 seconds to accumulate statistics ====")
        sleep(5)

        log.info("==== Disconnect all inputs and check stats ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.disconnectAll()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), numInputs)
        for ARINC429Stat in response.body.status:
            # All channels just got disconnected from output 3
            self.assertEqual(ARINC429Stat.conState, ARINC429Response.DISCONNECTED)
            self.assertEqual(ARINC429Stat.source, "ARINC_429_TX3")
            if ARINC429Stat.sink == "ARINC_429_RX5" or ARINC429Stat.sink == "ARINC_429_RX6":
                self.assertGreater(ARINC429Stat.xmtCount, 0)
                self.assertGreaterEqual(ARINC429Stat.xmtCount, ARINC429Stat.rcvCount)
                self.assertGreaterEqual(ARINC429Stat.errorCount, 0)
            else:
                self.assertGreater(ARINC429Stat.xmtCount, 0)
                self.assertEqual(ARINC429Stat.rcvCount, 0)
                self.assertGreater(ARINC429Stat.errorCount, 0)

        log.info("==== Report on all inputs after disconnect ====")
        response = module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportAll()))
        self.assertEqual(response.name, "ARINC429Response")
        self.assertEqual(len(response.body.status), numInputs)
        for ARINC429Stat in response.body.status:
            # All channels disconnected again
            self.assertEqual(ARINC429Stat.conState, ARINC429Response.DISCONNECTED)
            self.assertEqual(ARINC429Stat.source, "")
        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond