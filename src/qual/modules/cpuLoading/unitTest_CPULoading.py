import unittest
from time import sleep

import CPULoading
from common.gpb.python import CPULoading_pb2
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger

## CPULoading Unit Test
#
class Test_CPULoading(unittest.TestCase):
    def test_basic(self):
        log = Logger(name='Test CPULoading')
        log.info('Running functionality test for CPULoading module:')
        self.module = CPULoading.CPULoading()

        message = CPULoading_pb2.CPULoadingRequest()
        sleep(3)

        ## test REPORT before CPU load
        log.info("REPORT before CPU load:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage(message)
        out = self.module.msgHandler(request)
        sleep(3)

        ## test RUN message with default level input and report
        log.info("RUN with default level and report:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.RUN
        request = ThalesZMQMessage(message)
        out = self.module.msgHandler(request)
        sleep(3)

        ## test REPORT message input after CPU load
        log.info("REPORT after CPU load:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage(message)
        out = self.module.msgHandler(request)
        sleep(3)

        ## test additional RUN with custom level
        log.info("RUN again with custom level while previous load running:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.RUN
        message.level = 50
        request = ThalesZMQMessage(message)
        out = self.module.msgHandler(request)
        sleep(3)

        ## test REPORT message input after additional RUN and custom level
        log.info("REPORT after starting additional load with custom level:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage(message)
        out = self.module.msgHandler(request)
        sleep(3)

        ## test STOP message input and report
        log.info("STOP and report:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.STOP
        request = ThalesZMQMessage(message)
        out = self.module.msgHandler(request)
        sleep(3)

        ## test REPORT message input after CPU load stop
        log.info("REPORT after stopping load:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage(message)
        out = self.module.msgHandler(request)
        sleep(3)

        ## test STOP with no load
        log.info("STOP with no load:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.STOP
        request = ThalesZMQMessage(message)
        out = self.module.msgHandler(request)
        sleep(3)

        ## test REPORT message input after stopping with no load
        log.info("REPORT after stopping with no load:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage(message)
        out = self.module.msgHandler(request)
        sleep(3)

        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()