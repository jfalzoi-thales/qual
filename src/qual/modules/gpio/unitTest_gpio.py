import unittest
from time import sleep

import gpio
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.GPIO_pb2 import GPIORequest
from common.logger.logger import Logger
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
                ("Disconnect all inputs",          GPIOMessages.disconnectAll)]

    @staticmethod
    def reportIn1():
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "PA_KYLN_IN1"
        return message

    @staticmethod
    def reportIn2():
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "PA_KYLN_IN2"
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
        message.gpIn = "PA_KYLN_IN1"
        message.gpOut = "VA_KYLN_OUT1"
        return message

    @staticmethod
    def connectIn2Out1():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "PA_KYLN_IN2"
        message.gpOut = "VA_KYLN_OUT1"
        return message

    @staticmethod
    def connectIn2Out2():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "PA_KYLN_IN2"
        message.gpOut = "VA_KYLN_OUT2"
        return message

    @staticmethod
    def connectInAllOut3():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "ALL"
        message.gpOut = "VA_KYLN_OUT3"
        return message

    @staticmethod
    def disconnectIn1():
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
        message.gpIn = "PA_BOGUS_IN2"
        message.gpOut = "VA_KYLN_OUT2"
        return message

    @staticmethod
    def connectOutBogus():
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "PA_KYLN_IN2"
        message.gpOut = "VA_BOGUS_OUT2"
        return message

    ## Constructor (not used)
    #  @param     self
    def __init__(self):
        super(GPIOMessages, self).__init__()


## GPIO Unit Test
class Test_GPIO(unittest.TestCase):
    def test_basic(self):
        log = Logger(name='Test GPIO')
        log.info('Running functionality test for GPIO module:')
        self.module = gpio.GPIO()

        log.info("==== Report before connecting ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.reportIn1()))
        sleep(1)

        log.info("==== Connect linked pair ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.connectIn1Out1()))
        sleep(1)

        log.info("==== Connect second pin to same output ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.connectIn2Out1()))
        sleep(1)

        log.info("==== Try to reconnect connected pin ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.connectIn2Out2()))
        sleep(1)

        log.info("==== Bogus input pin specified ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.connectInBogus()))
        sleep(1)

        log.info("==== Bogus output pin specified ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.connectOutBogus()))
        sleep(1)

        log.info("==== Report on non-linked input ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.reportIn2()))
        sleep(1)

        log.info("==== Report on all inputs ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.reportAll()))
        sleep(1)

        log.info("==== Disconnect linked input ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.disconnectIn1()))
        sleep(1)

        log.info("==== Connect all inputs ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.connectInAllOut3()))
        sleep(4)

        log.info("==== Report on all inputs ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.reportAll()))
        sleep(2)

        log.info("==== Disconnect all inputs ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.disconnectAll()))
        sleep(1)

        log.info("==== Report on all inputs ====")
        self.module.msgHandler(ThalesZMQMessage(GPIOMessages.reportAll()))
        sleep(1)

        log.info("Terminating module...")
        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond
