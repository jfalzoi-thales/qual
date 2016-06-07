import unittest
from time import sleep

import systemMonitoring
from common.gpb.python.SystemMonitoring_pb2 import SystemMonitoringRequest
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## SystemMonitoring Messages
class SystemMonitoringMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "System Monitoring"

    @staticmethod
    def getMenuItems():
        return [("Report",  SystemMonitoringMessages.report),]

    @staticmethod
    def report():
        message = SystemMonitoringRequest()
        return message


## SystemMonitoring Unit Test
class Test_SystemMonitoring(unittest.TestCase):
    ## Basic functionality test for SystemMonitoring module
    #  @param     self
    def test_basic(self):
        log = Logger(name='Test SystemMonitoring')
        log.info('Running functionality test for SystemMonitoring module:')
        self.module = systemMonitoring.SystemMonitoring()

        log.info("REPORT current SystemMonitoring information:")
        self.module.msgHandler(ThalesZMQMessage(SystemMonitoringMessages.report()))
        sleep(3)

        log.info("REPORT current SystemMonitoring information again:")
        self.module.msgHandler(ThalesZMQMessage(SystemMonitoringMessages.report()))

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond
