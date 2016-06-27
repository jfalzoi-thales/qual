import unittest

import systemMonitoring
from common.gpb.python.SystemMonitoring_pb2 import SystemMonitoringRequest, SystemMonitoringResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger import logger
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
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the SystemMonitoring test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = logger.Logger(name='Test SystemMonitoring')
        cls.log.info('++++ Setup before SystemMonitoring module unit tests ++++')
        # Create the module
        cls.module = systemMonitoring.SystemMonitoring()
        # Uncomment this if you don't want to see module debug messages
        #cls.module.log.setLevel(logger.INFO)

    ## Test case: Send SystemMonitoring request
    # SystemMonitoringRequest does not take any parameters, so we just send
    # the request, and check that the response fields are present.
    # We send the request twice and be sure we get a valid response both times.
    #  @param     self
    def test_request(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Check for valid SystemMonitoringResponse ****")
        for i in range(1,3):
            log.info("==== Iteration %d ====" % i)
            response = module.msgHandler(ThalesZMQMessage(SystemMonitoringMessages.report()))
            self.assertEqual(response.name, "SystemMonitoringResponse")
            self.assertGreater(len(response.body.powerSupplyStatistics), 0)
            self.assertGreater(len(response.body.semaStatistics), 0)
            self.assertGreater(len(response.body.switchData.temperature), 0)
            self.assertGreater(len(response.body.switchData.statistics), 0)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
