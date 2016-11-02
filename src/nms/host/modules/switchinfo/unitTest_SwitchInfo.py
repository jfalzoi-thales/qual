import unittest

from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from nms.host.pb2.nms_host_api_pb2 import SwitchInfoReq
from switchInfo import SwitchInfo
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## SwitchInfo Messages
class SwitchInfoMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Switch Info"

    @staticmethod
    def getMenuItems():
        return [("Request info",   SwitchInfoMessages.info)]

    @staticmethod
    def info():
        message = SwitchInfoReq()
        return message


## SwitchInfo Unit Test
class Test_SwitchInfo(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the Config Port State test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test Switch Info')
        cls.log.info('++++ Setup before Switch Info module unit tests ++++')
        # Create the module
        cls.module = SwitchInfo()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Valid Test case
    #
    #   Send a BLOCKING Message
    def test_Block(self):
        log = self.__class__.log
        module = self.__class__.module

        response = module.msgHandler(ThalesZMQMessage(SwitchInfoMessages.info()))
        self.assertEqual(response.name, "SwitchInfoResp")
        self.assertEqual(response.body.success, True)
        # Get the temperature from the response
        tempResp = response.body.values[0]
        self.assertEqual(tempResp.key, "temperature")
        self.assertNotEqual(tempResp.value, "")
        log.info("==== Test complete ====")


if __name__ == '__main__':
    ConfigurableObject.setFilename("HNMS")
    unittest.main()

## @endcond
