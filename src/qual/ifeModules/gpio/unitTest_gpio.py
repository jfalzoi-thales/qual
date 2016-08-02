import unittest
import gpio
from common.gpb.python.GPIOManager_pb2 import RequestMessage, ResponseMessage
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

#  @cond doxygen_unittest

## IFEGPIO Messages
class IFEGPIOMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "IFE-GPIO"

    @staticmethod
    def getMenuItems():
        return [("Get value", IFEGPIOMessages.get),
                ("Set value", IFEGPIOMessages.set)]

    @staticmethod
    def get():
        message = RequestMessage()
        message.request_type = RequestMessage.GET
        message.pin_name = "LLS_IN_GP_KL_02"
        return message

    @staticmethod
    def set():
        message = RequestMessage()
        message.request_type = RequestMessage.SET
        message.pin_name = "LLS_OUT_GP_KL_01"
        message.value = True
        return message


## IFEGPIO Unit Test
class Test_IFEGPIO(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the IFEGPIO test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test IFE-GPIO')
        cls.log.info('++++ Setup before IFE-GPIO module unit tests ++++')
        # Create the module
        cls.module = gpio.IFEGPIO()
        # Uncomment this if you want to see module debug messages
        #cls.module.log.setLevel("DEBUG")

    ## Test case: Try to get a  value
    def test_get(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get value ****")
        response = module.msgHandler(ThalesZMQMessage(IFEGPIOMessages.get()))
        self.assertEqual(response.body.error, ResponseMessage.OK)
        self.assertEqual(response.body.pin_name, "LLS_IN_GP_KL_02")
        log.info("==== Test complete ====")

    ## Test case: Try to set a  value
    def test_set(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Set value ****")
        response = module.msgHandler(ThalesZMQMessage(IFEGPIOMessages.set()))
        self.assertEqual(response.body.error, ResponseMessage.OK)
        self.assertEqual(response.body.pin_name, "LLS_OUT_GP_KL_01")
        self.assertEqual(response.body.state, True)
        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
