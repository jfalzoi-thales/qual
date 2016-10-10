import os
import unittest
from time import sleep

import gpio
from qual.pb2.GPIO_pb2 import GPIORequest, GPIOResponse
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger import logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


# @cond doxygen_unittest

## GPIO Messages
class GPIOMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "GPIO"

    @staticmethod
    def getMenuItems():
        if os.path.isfile("/dev/mps/usb-mcp2221-ife"):
            items = [("Report for input 1", GPIOMessages.reportIn1),
                    ("Report for input 2", GPIOMessages.reportIn2),
                    ("Report for input 7", GPIOMessages.reportIn7),
                    ("Report for PA input 1", GPIOMessages.reportPAIn1),
                    ("Report for PA Mute", GPIOMessages.reportPAMute),
                    ("Report for all inputs", GPIOMessages.reportAll),
                    ("Connect input 1 to output 1", GPIOMessages.connectIn1Out1),
                    ("Connect input 2 to output 1", GPIOMessages.connectIn2Out1),
                    ("Connect input 2 to output 2", GPIOMessages.connectIn2Out2),
                    ("Connect input 7 to output 7", GPIOMessages.connectIn7Out7),
                    ("Connect PA input 1 to VA output 1", GPIOMessages.connectPAIn1VAOut1),
                    ("Connect all inputs to output 3", GPIOMessages.connectInAllOut3),
                    ("Disconnect input 1", GPIOMessages.disconnectIn1),
                    ("Disconnect input 2", GPIOMessages.disconnectIn2),
                    ("Disconnect input 7", GPIOMessages.disconnectIn7),
                    ("Disconnect PA input 1", GPIOMessages.disconnectPAIn1),
                    ("Disconnect all inputs", GPIOMessages.disconnectAll)]
        else:
            items = [("Report for input 1", GPIOMessages.reportIn1),
                     ("Report for input 2", GPIOMessages.reportIn2),
                     ("Report for all inputs", GPIOMessages.reportAll),
                     ("Connect input 1 to output 1", GPIOMessages.connectIn1Out1),
                     ("Connect input 2 to output 1", GPIOMessages.connectIn2Out1),
                     ("Connect input 2 to output 2", GPIOMessages.connectIn2Out2),
                     ("Connect all inputs to output 3", GPIOMessages.connectInAllOut3),
                     ("Disconnect input 1", GPIOMessages.disconnectIn1),
                     ("Disconnect input 2", GPIOMessages.disconnectIn2),
                     ("Disconnect all inputs", GPIOMessages.disconnectAll)]

        return items

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
    def reportIn7():
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "GP_KYLN_IN7"
        return message

    @staticmethod
    def reportPAIn1():
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "PA_KYLN_IN1"
        return message

    @staticmethod
    def reportPAMute():
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "PA_MUTE_KYLN_IN"
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
    def connectIn7Out7():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "GP_KYLN_IN7"
        message.gpOut = "GP_KYLN_OUT7"
        return message

    @staticmethod
    def connectPAIn1VAOut1():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "PA_KYLN_IN1"
        message.gpOut = "VA_KYLN_OUT1"
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
    def disconnectIn7():
        message = GPIORequest()
        message.requestType = GPIORequest.DISCONNECT
        message.gpIn = "GP_KYLN_IN7"
        return message

    @staticmethod
    def disconnectPAIn1():
        message = GPIORequest()
        message.requestType = GPIORequest.DISCONNECT
        message.gpIn = "PA_KYLN_IN1"
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

    @staticmethod
    def connectMapping(map):
        messages = []

        for input, output in map.items():
            message = GPIORequest()
            message.requestType = GPIORequest.CONNECT
            message.gpIn = input
            message.gpOut = output
            messages.append(message)

        return messages

    @staticmethod
    def swapPins():
        messages = []

        message = GPIORequest()
        message.requestType = GPIORequest.DISCONNECT
        message.gpIn = "GP_KYLN_IN5"
        messages.append(message)

        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "GP_KYLN_IN5"
        message.gpOut = "GP_KYLN_OUT6"
        messages.append(message)

        return messages

    @staticmethod
    def reportIn5():
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "GP_KYLN_IN5"
        return message

    ## Constructor (not used)
    #  @param     self
    def __init__(self):
        super(GPIOMessages, self).__init__()


## GPIO Unit Test
class Test_GPIO(unittest.TestCase):
    ## Static ife flag instance
    ife = None
    ## Static logger instance
    log = None
    ## Static module instance
    module = None

    ## Setup for the GPIO test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        # Flag to detect if running on MPSi
        cls.ife = os.path.isfile("/dev/mps/usb-mcp2221-ife")
        # Create a logger so we can add details to a multi-step test case
        cls.log = logger.Logger(name='Test GPIO')
        cls.log.info('++++ Setup before GPIO module unit tests ++++')
        # Create the module
        if cls.module is None:
            cls.module = gpio.GPIO()

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
        # Sleep a bit to allow GPIO background thread to process disconnect
        sleep(1)

    ## Test case: Try to connect an invalid input pin
    # Should return an empty GPIOResponse
    def ftest_invalidInput(self):
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
    def ftest_invalidOutput(self):
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
    def ftest_reconnect(self):
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
    # This test case will connect a "linked" pair, wait 5 seconds, then
    # verify that the report indicates 2-3 matches and 0 mismatches.
    # It also verifies that the report is cleared when read back
    # after a disconnect.
    def ftest_linkedPair(self):
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
        self.assertGreater(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN1")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT1")

        log.info("==== Disconnect connected pair ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.disconnectIn1()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
        self.assertGreater(response.body.status[0].matchCount, 0)
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

    ## Test case: Connect an IFE card input/output pair
    # This test case will connect two IFE card pins, wait 5 seconds, then
    # verify that the report indicates 2-3 matches and 0 mismatches.
    def ftest_ifeCardPair(self):
        ife = self.__class__.ife
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Connect an IFE input/output pair ****")

        if ife:
            log.info("==== Report before connecting ====")
            response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportIn7()))
            self.assertEqual(response.name, "GPIOResponse")
            self.assertEqual(len(response.body.status), 1)
            self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
            self.assertEqual(response.body.status[0].matchCount, 0)
            self.assertEqual(response.body.status[0].mismatchCount, 0)
            self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN7")
            self.assertEqual(response.body.status[0].gpOut, "")

            log.info("==== Connect IFE pair ====")
            response = module.msgHandler(ThalesZMQMessage(GPIOMessages.connectIn7Out7()))
            self.assertEqual(response.name, "GPIOResponse")
            self.assertEqual(len(response.body.status), 1)
            self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
            self.assertEqual(response.body.status[0].matchCount, 0)
            self.assertEqual(response.body.status[0].mismatchCount, 0)
            self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN7")
            self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT7")

            log.info("==== Wait 5 seconds to accumulate statistics ====")
            sleep(5)

            log.info("==== Get report after 5 seconds ====")
            response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportIn7()))
            self.assertEqual(response.name, "GPIOResponse")
            self.assertEqual(len(response.body.status), 1)
            self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
            self.assertGreater(response.body.status[0].matchCount, 0)
            self.assertEqual(response.body.status[0].mismatchCount, 0)
            self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN7")
            self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT7")

            log.info("==== Disconnect connected pair ====")
            response = module.msgHandler(ThalesZMQMessage(GPIOMessages.disconnectIn7()))
            self.assertEqual(response.name, "GPIOResponse")
            self.assertEqual(len(response.body.status), 1)
            self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
            self.assertGreater(response.body.status[0].matchCount, 0)
            self.assertEqual(response.body.status[0].mismatchCount, 0)
            self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN7")
            self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT7")
            log.info("==== Test complete ====")
        else:
            log.info("IFE functionality not enabled on this device")

    ## Test case: Connect an IFE PAVA input/output pair
    # This test case will connect two IFE PAVA pins, wait 5 seconds, then
    # verify that the report indicates 2-3 matches and 0 mismatches.
    def ftest_ifePAVAPair(self):
        ife = self.__class__.ife
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Connect an IFE PAVA input/output pair ****")

        if ife:
            log.info("==== Report before connecting ====")
            response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportPAIn1()))
            self.assertEqual(response.name, "GPIOResponse")
            self.assertEqual(len(response.body.status), 1)
            self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
            self.assertEqual(response.body.status[0].matchCount, 0)
            self.assertEqual(response.body.status[0].mismatchCount, 0)
            self.assertEqual(response.body.status[0].gpIn, "PA_KYLN_IN1")
            self.assertEqual(response.body.status[0].gpOut, "")

            log.info("==== Connect IFE PAVA pair ====")
            response = module.msgHandler(ThalesZMQMessage(GPIOMessages.connectPAIn1VAOut1()))
            self.assertEqual(response.name, "GPIOResponse")
            self.assertEqual(len(response.body.status), 1)
            self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
            self.assertEqual(response.body.status[0].matchCount, 0)
            self.assertEqual(response.body.status[0].mismatchCount, 0)
            self.assertEqual(response.body.status[0].gpIn, "PA_KYLN_IN1")
            self.assertEqual(response.body.status[0].gpOut, "VA_KYLN_OUT1")

            log.info("==== Wait 5 seconds to accumulate statistics ====")
            sleep(5)

            log.info("==== Get report after 5 seconds ====")
            response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportPAIn1()))
            self.assertEqual(response.name, "GPIOResponse")
            self.assertEqual(len(response.body.status), 1)
            self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
            self.assertGreater(response.body.status[0].matchCount, 0)
            self.assertEqual(response.body.status[0].mismatchCount, 0)
            self.assertEqual(response.body.status[0].gpIn, "PA_KYLN_IN1")
            self.assertEqual(response.body.status[0].gpOut, "VA_KYLN_OUT1")

            log.info("==== Disconnect connected PAVA pair ====")
            response = module.msgHandler(ThalesZMQMessage(GPIOMessages.disconnectPAIn1()))
            self.assertEqual(response.name, "GPIOResponse")
            self.assertEqual(len(response.body.status), 1)
            self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
            self.assertGreater(response.body.status[0].matchCount, 0)
            self.assertEqual(response.body.status[0].mismatchCount, 0)
            self.assertEqual(response.body.status[0].gpIn, "PA_KYLN_IN1")
            self.assertEqual(response.body.status[0].gpOut, "VA_KYLN_OUT1")
            log.info("==== Test complete ====")
        else:
            log.info("IFE functionality not enabled on this device")

    ## Test case: Report on PA Mute
    def ftest_ifePAMute(self):
        ife = self.__class__.ife
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Report on PA Mute ****")

        if ife:
            response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportPAMute()))
            self.assertEqual(response.name, "GPIOResponse")
            self.assertEqual(len(response.body.status), 1)
            self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
            self.assertEqual(response.body.status[0].matchCount, 0)
            self.assertEqual(response.body.status[0].mismatchCount, 0)
            self.assertEqual(response.body.status[0].gpIn, "PA_MUTE_KYLN_IN")
        else:
            log.info("IFE functionality not enabled on this device")

    ## Test case: Connect an unlinked input/output pair
    # This test case will connect an "unlinked" pair, wait 5 seconds, then
    # verify that the report indicates 0 matches and 2-3 mismatches.
    def ftest_unlinkedPair(self):
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
        self.assertGreater(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN2")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT1")
        log.info("==== Test complete ====")

    ## Test case: Use of the "ALL" parameter
    # Tests CONNECT, DISCONNECT, and REPORT messages with the input
    # pin specified as "ALL" perform the correct actions.
    def ftest_allparam(self):
        ife = self.__class__.ife
        log = self.__class__.log
        module = self.__class__.module

        numInputs = 19 if ife else 6

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
                self.assertGreater(gpioStat.matchCount, 0)
                self.assertEqual(gpioStat.mismatchCount, 0)
            else:
                self.assertEqual(gpioStat.matchCount, 0)
                self.assertGreater(gpioStat.mismatchCount, 0)

        log.info("==== Report on all inputs after disconnect ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportAll()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), numInputs)
        for gpioStat in response.body.status:
            # All pins disconnected again
            self.assertEqual(gpioStat.conState, GPIOResponse.DISCONNECTED)
            self.assertEqual(gpioStat.gpOut, "")
        log.info("==== Test complete ====")

    ## Test case: Test mapping defined by test equipment
    def test_mapping(self):
        ife = self.__class__.ife
        log = self.__class__.log
        module = self.__class__.module

        if ife:
            map = {"GP_KYLN_IN1": "GP_KYLN_OUT1",
                   "GP_KYLN_IN2": "GP_KYLN_OUT2",
                   "GP_KYLN_IN3": "GP_KYLN_OUT3",
                   "GP_KYLN_IN4": "GP_KYLN_OUT4",
                   "GP_KYLN_IN5": "GP_KYLN_OUT5",
                   "GP_KYLN_IN6": "GP_KYLN_OUT7",
                   "GP_KYLN_IN7": "GP_KYLN_OUT7",
                   "GP_KYLN_IN8": "GP_KYLN_OUT8",
                   "GP_KYLN_IN9": "GP_KYLN_OUT9",
                   "PA_KYLN_IN1": "VA_KYLN_OUT1",
                   "PA_KYLN_IN2": "VA_KYLN_OUT2",
                   "PA_KYLN_IN3": "VA_KYLN_OUT3",
                   "PA_KYLN_IN4": "VA_KYLN_OUT4",
                   "PA_KYLN_IN5": "VA_KYLN_OUT5",
                   "PA_KYLN_IN6": "VA_KYLN_OUT6",
                   "PA_KYLN_IN7": "VA_KYLN_OUT6",
                   "PA_KYLN_IN8": "VA_KYLN_OUT6"}
        else:
            map = {"GP_KYLN_IN1": "GP_KYLN_OUT1",
                   "GP_KYLN_IN2": "GP_KYLN_OUT2",
                   "GP_KYLN_IN3": "GP_KYLN_OUT3",
                   "GP_KYLN_IN4": "GP_KYLN_OUT4",
                   "GP_KYLN_IN5": "GP_KYLN_OUT5"}

        log.info("**** Test case: Test Mapping Defined by Test Equipment ****")
        log.info("==== Connect Mapped Channels ====")
        messages = GPIOMessages.connectMapping(map)

        for message in messages:
            response = module.msgHandler(ThalesZMQMessage(message))
            self.assertEqual(response.name, "GPIOResponse")
            self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
            self.assertEqual(response.body.status[0].matchCount, 0)
            self.assertEqual(response.body.status[0].mismatchCount, 0)
            self.assertEqual(response.body.status[0].gpIn, message.gpIn)
            self.assertEqual(response.body.status[0].gpOut, message.gpOut)

        log.info("==== Wait 5 Seconds to Accumulate Statistics ====")
        sleep(5)

        log.info("==== Report on All Inputs ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportAll()))
        self.assertEqual(response.name, "GPIOResponse")

        for gpioStat in response.body.status:
            if gpioStat.gpIn not in ["PA_ALL_KYLN_IN", "PA_MUTE_KYLN_IN"]:
                self.assertEqual(gpioStat.conState, GPIOResponse.CONNECTED)
                self.assertGreater(gpioStat.matchCount, 0)
                self.assertEqual(gpioStat.mismatchCount, 0)
                self.assertTrue(gpioStat.gpIn in map)
                self.assertEqual(gpioStat.gpOut, map[gpioStat.gpIn])
            else:
                self.assertEqual(gpioStat.conState, GPIOResponse.DISCONNECTED)
                self.assertEqual(gpioStat.matchCount, 0)
                self.assertEqual(gpioStat.mismatchCount, 0)
                self.assertTrue(gpioStat.gpIn in ["PA_ALL_KYLN_IN", "PA_MUTE_KYLN_IN"])
                self.assertEqual(gpioStat.gpOut, "")

        log.info("==== Swap GP_KYLN_OUT5 Pin For GP_KYLN_OUT6 ====")
        messages = GPIOMessages.swapPins()

        response = module.msgHandler(ThalesZMQMessage(messages[0]))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(response.body.status[0].conState, GPIOResponse.DISCONNECTED)
        self.assertGreater(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN5")

        response = module.msgHandler(ThalesZMQMessage(messages[1]))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
        self.assertEqual(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN5")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT6")

        log.info("==== Wait 5 Seconds to Accumulate Statistics ====")
        sleep(5)

        log.info("==== Get Report on GP_KYLN_IN5 ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.reportIn5()))
        self.assertEqual(response.name, "GPIOResponse")
        self.assertEqual(len(response.body.status), 1)
        self.assertEqual(response.body.status[0].conState, GPIOResponse.CONNECTED)
        self.assertGreater(response.body.status[0].matchCount, 0)
        self.assertEqual(response.body.status[0].mismatchCount, 0)
        self.assertEqual(response.body.status[0].gpIn, "GP_KYLN_IN5")
        self.assertEqual(response.body.status[0].gpOut, "GP_KYLN_OUT6")

        log.info("==== Disconnect All Inputs ====")
        response = module.msgHandler(ThalesZMQMessage(GPIOMessages.disconnectAll()))
        self.assertEqual(response.name, "GPIOResponse")

        for gpioStat in response.body.status:
            self.assertEqual(gpioStat.conState, GPIOResponse.DISCONNECTED)
            self.assertEqual(gpioStat.mismatchCount, 0)

            if gpioStat.gpIn not in ["PA_ALL_KYLN_IN", "PA_MUTE_KYLN_IN"]:
                self.assertGreater(gpioStat.matchCount, 0)

                if (gpioStat.gpIn == "GP_KYLN_IN5"):
                    self.assertEqual(gpioStat.gpIn, "GP_KYLN_IN5")
                    self.assertEqual(gpioStat.gpOut, "GP_KYLN_OUT6")
                else:
                    self.assertTrue(gpioStat.gpIn in map)
                    self.assertEqual(gpioStat.gpOut, map[gpioStat.gpIn])
            else:
                self.assertEqual(gpioStat.matchCount, 0)
                self.assertTrue(gpioStat.gpIn in ["PA_ALL_KYLN_IN", "PA_MUTE_KYLN_IN"])
                self.assertEqual(gpioStat.gpOut, "")

if __name__ == '__main__':
    unittest.main()

## @endcond
