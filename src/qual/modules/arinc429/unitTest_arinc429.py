import unittest
from time import sleep

import arinc429
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.ARINC429_pb2 import ARINC429Request
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

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
    def disconnectAll():
        message = ARINC429Request()
        message.requestType = ARINC429Request.DISCONNECT
        message.sink = "ALL"
        return message

    @staticmethod
    def connectInBogus():
        message = ARINC429Request()
        message.requestType = ARINC429Request.CONNECT
        message.sink = "PA_BOGUS_IN2"
        message.source = "ARINC_429_TX2"
        return message

    @staticmethod
    def connectOutBogus():
        message = ARINC429Request()
        message.requestType = ARINC429Request.CONNECT
        message.sink = "ARINC_429_RX2"
        message.source = "VA_BOGUS_OUT2"
        return message

    ## Constructor (not used)
    #  @param     self
    def __init__(self):
        super(ARINC429Messages, self).__init__()

## ARINC429 Unit Test
class Test_ARINC429(unittest.TestCase):
    def test_basic(self):
        log = Logger(name='Test ARINC429')
        log.info('Running functionality test for ARINC429 module:')
        self.module = arinc429.ARINC429()

        log.info("==== Report before connecting ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportIn1()))
        sleep(1)

        log.info("==== Connect linked pair ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectIn1Out1()))
        sleep(1)

        log.info("==== Connect third channel to same output ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectIn3Out1()))
        sleep(1)

        log.info("==== Try to reconnect connected channel ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectIn3Out2()))
        sleep(1)

        log.info("==== Bogus input channel specified ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectInBogus()))
        sleep(1)

        log.info("==== Bogus output channel specified ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectOutBogus()))
        sleep(1)

        log.info("==== Report on non-linked input ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportIn3()))
        sleep(1)

        log.info("==== Report on all inputs ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportAll()))
        sleep(1)

        log.info("==== Disconnect linked input ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.disconnectIn1()))
        sleep(1)

        log.info("==== Connect all inputs ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.connectInAllOut3()))
        sleep(4)

        log.info("==== Report on all inputs ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportAll()))
        sleep(2)

        log.info("==== Disconnect all inputs ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.disconnectAll()))
        sleep(1)

        log.info("==== Report on all inputs ====")
        self.module.msgHandler(ThalesZMQMessage(ARINC429Messages.reportAll()))
        sleep(1)

        log.info("Terminating module...")
        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond