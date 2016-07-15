import unittest
from time import sleep

import gpio
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.GPIO_pb2 import GPIORequest, GPIOResponse
from common.logger import logger
from common.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## GPIO Messages
class GPIOMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "GPIO"

    @staticmethod
    def getMenuItems():
        return [("Report for input 1",             GPIOMessages.reportIn1),
                ("Report for input 2",             GPIOMessages.reportIn2),
                ("Report for all inputs",          GPIOMessages.reportAll),
                ("Connect input 1 to output 1",    GPIOMessages.connectIn1Out1),
                ("Connect input 2 to output 1",    GPIOMessages.connectIn2Out1),
                ("Connect input 2 to output 2",    GPIOMessages.connectIn2Out2),
                ("Connect all inputs to output 3", GPIOMessages.connectInAllOut3),
                ("Disconnect input 1",             GPIOMessages.disconnectIn1),
                ("Disconnect input 2",             GPIOMessages.disconnectIn2),
                ("Disconnect all inputs",          GPIOMessages.disconnectAll)]

    @staticmethod
    def reportIn1():
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "GP_KYLN_IN1"
        return message

    @staticmethod
    def reportIn2():
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "GP_KYLN_IN2"
        return message

    @staticmethod
    def reportAll():
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "ALL"
        return message

    @staticmethod
    def connectIn1Out1():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "GP_KYLN_IN1"
        message.gpOut = "GP_KYLN_OUT1"
        return message

    @staticmethod
    def connectIn2Out1():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "GP_KYLN_IN2"
        message.gpOut = "GP_KYLN_OUT1"
        return message

    @staticmethod
    def connectIn2Out2():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "GP_KYLN_IN2"
        message.gpOut = "GP_KYLN_OUT2"
        return message

    @staticmethod
    def connectInAllOut3():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "ALL"
        message.gpOut = "GP_KYLN_OUT3"
        return message

    @staticmethod
    def disconnectIn1():
        message = GPIORequest()
        message.requestType = GPIORequest.DISCONNECT
        message.gpIn = "GP_KYLN_IN1"
        return message

    @staticmethod
    def disconnectIn2():
        message = GPIORequest()
        message.requestType = GPIORequest.DISCONNECT
        message.gpIn = "GP_KYLN_IN2"
        return message

    @staticmethod
    def disconnectAll():
        message = GPIORequest()
        message.requestType = GPIORequest.DISCONNECT
        message.gpIn = "ALL"
        return message

    @staticmethod
    def connectInBogus():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "GP_BOGUS_IN2"
        message.gpOut = "GP_KYLN_OUT2"
        return message

    @staticmethod
    def connectOutBogus():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "GP_KYLN_IN2"
        message.gpOut = "GP_BOGUS_OUT2"
        return message

    ## Constructor (not used)
    #  @param     self
    def __init__(self):
        super(GPIOMessages, self).__init__()


## GPIO Unit Test
class Test_GPIO(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the GPIO test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = logger.Logger(name='Test GPIO')
        cls.log.info('++++ Setup before GPIO module unit tests ++++')
        # Create the module
        cls.module = gpio.GPIO()
        # Uncomment this if you don't want to see module debug messages
        #cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with GPIO test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after GPIO module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(GPIOMessages.disconnectAll()))

    ## Test case: Try to connect an invalid input pin
    # Should return an empty GPIOResponse
    def test_invalidInput(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Invalid input pin specified ****")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.connectInBogus()))
        # Invalid input pin will return an empty GPIOResponse
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 0)
        log.info("==== Test complete ====")

    # Test case: Try to connect an invalid output pin
    # Should return an empty GPIOResponse
    def test_invalidOutput(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Invalid output pin specified ****")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.connectOutBogus()))
        # Invalid output pin will return an empty GPIOResponse
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 0)
        log.info("==== Test complete ====")

    ## Test case: Try to reconnect a connected input pin
    # Should return a GPIOResponse showing pin still connected to original output
    def test_reconnect(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Try to reconnect a connected input pin ****")
        log.info("==== Report before connecting ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportIn2()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
        self.assertEqual(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN2")
        self.assertEqual(response.body.status[0].gpOut, "")

        log.info("==== Connect input ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.connectIn2Out1()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
        self.assertEqual(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN2")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT1")

        log.info("==== Try to connect input to different output ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.connectIn2Out2()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
        self.assertEqual(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN2")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT1")
        log.info("==== Test complete ====")

    ## Test case: Connect a linked input/output pair
    # This test case will connect a "linked" pair, wait 4 seconds, then
    # verify that the report indicates 4-5 matches and 0 mismatches.
    # It also verifies that the report is cleared when read back
    # after a disconnect.
    def test_linkedPair(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Connect a linked input/output pair ****")
        log.info("==== Report before connecting ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportIn1()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
        self.assertEqual(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN1")
        self.assertEqual(response.body.status[0].gpOut, "")

        log.info("==== Connect linked pair ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.connectIn1Out1()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
        self.assertEqual(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN1")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT1")

        log.info("==== Wait 5 seconds to accumulate statistics ====")
        sleep(5)

        log.info("==== Get report after 5 seconds ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportIn1()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
        self.assertGreaterEqual(response.body.status[0].matchCount, 2)
        self.assertLessEqual(response.body.status[0].matchCount, 3)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN1")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT1")

        log.info("==== Disconnect connected pair ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.disconnectIn1()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
        self.assertGreaterEqual(response.body.status[0].matchCount, 2)
        self.assertLessEqual(response.body.status[0].matchCount, 3)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN1")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT1")

        log.info("==== Report after disconnect ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportIn1()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
        self.assertEqual(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN1")
        self.assertEqual(response.body.status[0].gpOut, "")
        log.info("==== Test complete ====")

    ## Test case: Connect an unlinked input/output pair
    # This test case will connect an "unlinked" pair, wait 4 seconds, then
    # verify that the report indicates 2-3 matches and 2-3 mismatches.
    def test_unlinkedPair(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Connect an unlinked input/output pair ****")
        log.info("==== Report before connecting ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportIn1()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
        self.assertEqual(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN1")
        self.assertEqual(response.body.status[0].gpOut, "")

        log.info("==== Connect unlinked pair ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.connectIn2Out1()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
        self.assertEqual(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN2")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT1")

        log.info("==== Wait 5 seconds to accumulate statistics ====")
        sleep(5)

        log.info("==== Disconnect connected pair and check results ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.disconnectIn2()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
        self.assertEqual(response.body.status[0].matchCount, 0)
        self.assertGreaterEqual(response.body.status[0].mismatchCount, 2)
        self.assertLessEqual(response.body.status[0].mismatchCount, 3)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN2")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT1")
        log.info("==== Test complete ====")

    ## Test case: Use of the "ALL" parameter
    # Tests CONNECT, DISCONNECT, and REPORT messages with the input
    # pin specified as "ALL" perform the correct actions.
    def test_allparam(self):
        log = self.__class__.log
        module = self.__class__.module

        numInputs = len(module.inputPins)

        log.info("**** Test case: Test use of the \"ALL\" parameter ****")
        log.info("==== Report on all inputs before connect ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportAll()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), numInputs)
        for gpioStat in response.body.status:
            # All pins should be disconnected
            self.assertEqual(gpioStat.conState, GPIOResponse.DISCONNECTED)
            self.assertEqual(gpioStat.gpOut, "")

        log.info("==== Connect all inputs ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.connectInAllOut3()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), numInputs)
        for gpioStat in response.body.status:
            # All pins should be connected to output 3
            self.assertEqual(gpioStat.conState, GPIOResponse.CONNECTED)
            self.assertEqual(gpioStat.gpOut, "GP_KYLN_OUT3")

        log.info("==== Report on all inputs after connect ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportAll()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), numInputs)
        for gpioStat in response.body.status:
            # All pins should still be connected to output 3
            self.assertEqual(gpioStat.conState, GPIOResponse.CONNECTED)
            self.assertEqual(gpioStat.gpOut, "GP_KYLN_OUT3")

        log.info("==== Wait 5 seconds to accumulate statistics ====")
        sleep(5)

        log.info("==== Disconnect all inputs and check stats ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.disconnectAll()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), numInputs)
        for gpioStat in response.body.status:
            # All pins just got disconnected from output 3
            self.assertEqual(gpioStat.conState, GPIOResponse.DISCONNECTED)
            self.assertEqual(gpioStat.gpOut, "GP_KYLN_OUT3")
            if (gpioStat.gpIn == "GP_KYLN_IN3"):
                self.assertGreaterEqual(gpioStat.matchCount, 2)
                self.assertEqual(gpioStat.mismatchCount, 0)
            else:
                self.assertEqual(gpioStat.matchCount, 0)
                self.assertGreaterEqual(gpioStat.mismatchCount, 2)

        log.info("==== Report on all inputs after disconnect ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportAll()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), numInputs)
        for gpioStat in response.body.status:
            # All pins disconnected again
            self.assertEqual(gpioStat.conState, GPIOResponse.DISCONNECTED)
            self.assertEqual(gpioStat.gpOut, "")
        log.info("==== Test complete ====")


if __name__ == '__main__':
    unittest.main()

## @endcond
