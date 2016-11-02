import unittest

import healthInfo
from nms.host.pb2.nms_host_api_pb2 import HealthInfoReq, HealthInfoResp
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


#  @cond doxygen_unittest

## HealthInfo Messages
class HealthInfoMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Health Info"

    @staticmethod
    def getMenuItems():
        return [("Get Health Information", HealthInfoMessages.getHealthInfo)]

    @staticmethod
    def getHealthInfo():
        message = HealthInfoReq()
        return message

## HealthInfo Unit Test
class Test_HealthInfo(unittest.TestCase):
    ## Static logger instance
    log = None
    ## Static module instance
    module = None

    ## Setup for the HealthInfo test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test HealthInfo')
        cls.log.info('++++ Setup before HealthInfo module unit tests ++++')
        # Create the module
        if cls.module is None:
            cls.module = healthInfo.HealthInfo()

    ## Teardown when done with HealthInfo test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after HealthInfo module unit tests ++++")
        cls.module.terminate()

    ## Test Case: Get Health Info
    def test_GetHealthInfo(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Test Case: Get Health Info ****")
        response = module.msgHandler(ThalesZMQMessage(HealthInfoMessages.getHealthInfo()))
        self.assertEqual(response.name, "HealthInfoResp")
        self.assertTrue(response.body.healthy)
        log.info("==== Test Complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
