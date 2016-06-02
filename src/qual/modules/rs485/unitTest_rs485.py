import unittest
import time

from qual.modules.rs485.rs485 import Rs485
from common.gpb.python import RS485_pb2
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger

## CPULoading Unit Test
#
class Test_RS485(unittest.TestCase):
    def test_basic(self):
        ## Logging the initialization
        log = Logger(name='Test RS485')
        log.info('Running test...')

        ## RS485 Module Object
        self.module = Rs485()

        ## Creating request message
        message = RS485_pb2.RS485Request()
        time.sleep(3)

        ## Send the REPORT message
        log.info("Send REPORT message before start running.")
        message.requestType = RS485_pb2.RS485Request.REPORT
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        time.sleep(3)

        ## Send the RUN message
        log.info("Send RUN message.")
        message.requestType = RS485_pb2.RS485Request.RUN
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        time.sleep(3)

        ## Send REPORT messages every 2 seconds
        for i in range(10):
            log.info("Sending REPORT message.")
            message.requestType = RS485_pb2.RS485Request.REPORT
            request = ThalesZMQMessage(message)
            self.module.msgHandler(request)
            time.sleep(2)

        ## Send the STOP message
        log.info("Sending STOP message.")
        message.requestType = RS485_pb2.RS485Request.STOP
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        time.sleep(3)

        ## Send the REPORT message
        log.info("Send REPORT message before start running.")
        message.requestType = RS485_pb2.RS485Request.REPORT
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        time.sleep(3)

        ## Send the RUN message
        log.info("Send RUN message.")
        message.requestType = RS485_pb2.RS485Request.RUN
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        time.sleep(3)

        ## Send REPORT messages every 2 seconds
        for i in range(10):
            log.info("Sending REPORT message.")
            message.requestType = RS485_pb2.RS485Request.REPORT
            request = ThalesZMQMessage(message)
            self.module.msgHandler(request)
            time.sleep(2)

        ## Send the STOP message
        log.info("Sending STOP message.")
        message.requestType = RS485_pb2.RS485Request.STOP
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        time.sleep(3)

        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()