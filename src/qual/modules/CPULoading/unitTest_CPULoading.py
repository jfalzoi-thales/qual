import unittest
from time import sleep

import CPULoading
from common.gpb.python import CPULoading_pb2
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger


class Test_CPULoading(unittest.TestCase):
    def test_basic(self):
        def testPrint(tzmq):
            log.info("Load Running: {} [0 is NO, 1 is YES]".format(tzmq.state))
            log.info("Total Untilization: {}".format(tzmq.totalUtilization))
            log.info("Core Untilization: {}\n".format(tzmq.coreUtilization))

        log = Logger(name='Test CPULoading')
        log.info('Running functionality test for CPULoading module:')
        self.module = CPULoading.CPULoading()

        message = CPULoading_pb2.CPULoadingRequest()
        sleep(3)

        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage("CPULoadingRequest", message)
        out = self.module.handler(request)

        log.info("REPORT before CPU load:")
        testPrint(out)
        sleep(3)

        ## test RUN message with default level input and report
        message.requestType = CPULoading_pb2.CPULoadingRequest.RUN
        request = ThalesZMQMessage("CPULoadingRequest", message)
        out = self.module.handler(request)

        log.info("RUN with default level and report:")
        testPrint(out)
        sleep(3)

        ## test REPORT message input after CPU load
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage("CPULoadingRequest", message)
        out = self.module.handler(request)

        log.info("REPORT after CPU load:")
        testPrint(out)
        sleep(3)

        ## test additional RUN with custom level
        message.requestType = CPULoading_pb2.CPULoadingRequest.RUN
        message.level = 50
        request = ThalesZMQMessage("CPULoadingRequest", message)
        out = self.module.handler(request)

        log.info("RUN again with custom level while previous load running:")
        testPrint(out)
        sleep(3)

        ## test REPORT message input after additional RUN and custom level
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage("CPULoadingRequest", message)
        out = self.module.handler(request)

        log.info("REPORT after starting additional load with custom level:")
        testPrint(out)
        sleep(3)

        ## test STOP message input and report
        message.requestType = CPULoading_pb2.CPULoadingRequest.STOP
        request = ThalesZMQMessage("CPULoadingRequest", message)
        out = self.module.handler(request)

        log.info("STOP and report:")
        testPrint(out)
        sleep(3)

        ## test REPORT message input after CPU load stop
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage("CPULoadingRequest", message)
        out = self.module.handler(request)

        log.info("REPORT after stopping load:")
        testPrint(out)
        sleep(3)

        ## test STOP with no load
        message.requestType = CPULoading_pb2.CPULoadingRequest.STOP
        request = ThalesZMQMessage("CPULoadingRequest", message)
        out = self.module.handler(request)

        log.info("STOP with no load:")
        testPrint(out)
        sleep(3)

        ## test REPORT message input after stopping with no load
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage("CPULoadingRequest", message)
        out = self.module.handler(request)

        log.info("REPORT after stopping with no load:")
        testPrint(out)
        sleep(3)

        self.module.terminate()
        
        pass

if __name__ == '__main__':
    unittest.main()