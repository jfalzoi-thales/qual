import unittest
from time import sleep

import systemMonitoring
from common.gpb.python.SystemMonitoring_pb2 import SystemMonitoringRequest
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger

# @cond doxygen_unittest

## SystemMonitoring Unit Test
class Test_Ethernet(unittest.TestCase):
    ## Basic functionality test for SystemMonitoring module
    #  @param     self
    def test_basic(self):
        log = Logger(name='Test SystemMonitoring')
        log.info('Running functionality test for SystemMonitoring module:')
        self.module = systemMonitoring.SystemMonitoring()

        message = SystemMonitoringRequest()
        sleep(3)

        #  test REPORT
        log.info("REPORT current SystemMonitoring information:")
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test additional REPORT
        log.info("REPORT current SystemMonitoring information again:")
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        pass

if __name__ == '__main__':
    unittest.main()
## @endcond