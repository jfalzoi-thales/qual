import unittest
from time import sleep

import gpio
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.GPIO_pb2 import GPIORequest
from common.logger.logger import Logger

# @cond doxygen_unittest

## GPIO Unit Test
#
class Test_Ethernet(unittest.TestCase):
    def test_basic(self):
        log = Logger(name='Test GPIO')
        log.info('Running functionality test for GPIO module:')
        self.module = gpio.GPIO()

        log.info("=============== Report before connecting ===============")
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "PA_KYLN_IN1"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(1)

        log.info("=============== Connect linked pair ===============")
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "PA_KYLN_IN1"
        message.gpOut = "VA_KYLN_OUT1"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(1)

        log.info("=============== Connect second pin to same output ===============")
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "PA_KYLN_IN2"
        message.gpOut = "VA_KYLN_OUT1"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(1)

        log.info("=============== Try to reconnect connected pin ===============")
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "PA_KYLN_IN2"
        message.gpOut = "VA_KYLN_OUT2"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(1)

        log.info("=============== Bogus input pin specified ===============")
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "PA_BOGUS_IN2"
        message.gpOut = "VA_KYLN_OUT2"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(1)

        log.info("=============== Bogus output pin specified ===============")
        message = GPIORequest()
        message.requestType = GPIORequest.CONNECT
        message.gpIn = "PA_KYLN_IN2"
        message.gpOut = "VA_BOGUS_OUT2"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(1)

        log.info("=============== Report on linked input ===============")
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "PA_KYLN_IN1"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(1)

        log.info("=============== Report on non-linked input ===============")
        message = GPIORequest()
        message.requestType = GPIORequest.REPORT
        message.gpIn = "PA_KYLN_IN2"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(1)

        log.info("=============== Disconnect linked input ===============")
        message = GPIORequest()
        message.requestType = GPIORequest.DISCONNECT
        message.gpIn = "PA_KYLN_IN1"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(1)

        log.info("=============== Disconnect non-linked input ===============")
        message = GPIORequest()
        message.requestType = GPIORequest.DISCONNECT
        message.gpIn = "PA_KYLN_IN2"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(1)

        log.info("Terminating module...")
        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond
