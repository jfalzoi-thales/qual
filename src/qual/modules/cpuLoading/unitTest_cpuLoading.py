import unittest
from time import sleep

import cpuLoading
from common.gpb.python.CPULoading_pb2 import CPULoadingRequest
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

#  @cond doxygen_unittest

## CPULoading Messages
class CPULoadingMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "CPU Loading"

    @staticmethod
    def getMenuItems():
        return [("Report",                   CPULoadingMessages.report),
                ("Run - default load (80%)", CPULoadingMessages.runDefault),
                ("Run - 50% load",           CPULoadingMessages.run50),
                ("Stop",                     CPULoadingMessages.stop)]

    @staticmethod
    def report():
        message = CPULoadingRequest()
        message.requestType = CPULoadingRequest.REPORT
        return message

    @staticmethod
    def runDefault():
        message = CPULoadingRequest()
        message.requestType = CPULoadingRequest.RUN
        return message

    @staticmethod
    def run50():
        message = CPULoadingRequest()
        message.requestType = CPULoadingRequest.RUN
        message.level = 50
        return message

    @staticmethod
    def stop():
        message = CPULoadingRequest()
        message.requestType = CPULoadingRequest.STOP
        return message

## CPULoading Unit Test
class Test_CPULoading(unittest.TestCase):
    def test_basic(self):
        log = Logger(name='Test CPU Loading')
        log.info('Running functionality test for CPULoading module:')

        self.module = cpuLoading.CPULoading()
        sleep(1)

        log.info("REPORT before CPU load:")
        self.module.msgHandler(ThalesZMQMessage(CPULoadingMessages.report()))
        sleep(3)

        log.info("RUN with default level and report:")
        self.module.msgHandler(ThalesZMQMessage(CPULoadingMessages.runDefault()))
        sleep(3)

        log.info("REPORT after CPU load:")
        self.module.msgHandler(ThalesZMQMessage(CPULoadingMessages.report()))
        sleep(3)

        log.info("RUN again with custom level while previous load running:")
        self.module.msgHandler(ThalesZMQMessage(CPULoadingMessages.run50()))
        sleep(3)

        log.info("REPORT after starting additional load with custom level:")
        self.module.msgHandler(ThalesZMQMessage(CPULoadingMessages.report()))
        sleep(3)

        log.info("STOP and report:")
        self.module.msgHandler(ThalesZMQMessage(CPULoadingMessages.stop()))
        sleep(3)

        log.info("REPORT after stopping load:")
        self.module.msgHandler(ThalesZMQMessage(CPULoadingMessages.report()))
        sleep(3)

        log.info("STOP with no load:")
        self.module.msgHandler(ThalesZMQMessage(CPULoadingMessages.stop()))
        sleep(3)

        log.info("REPORT after stopping with no load:")
        self.module.msgHandler(ThalesZMQMessage(CPULoadingMessages.report()))
        sleep(3)

        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond