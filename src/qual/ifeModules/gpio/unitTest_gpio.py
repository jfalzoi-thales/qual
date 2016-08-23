import unittest
from time import sleep
import gpio
from common.gpb.python.GPIOManager_pb2 import RequestMessage, ResponseMessage, INPUT, OUTPUT
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## IFEGPIO handler tester class
class IFEGPIOMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "GPIO for IFE"

    @staticmethod
    def getMenuItems():
        return [("Set", RequestMessage.setAll),
                ("Get", RequestMessage.getAll)]

    @staticmethod
    def setAll():
        messageList = []

        for pin in ["LLS_OUT_GP_KL_01", "LLS_OUT_GP_KL_02", "LLS_OUT_GP_KL_03",
                           "VA_KLOUT1", "VA_KLOUT2", "VA_KLOUT3", "VA_KLOUT4", "VA_KLOUT5", "VA_KLOUT6"]:
            message = RequestMessage()
            message.pin_name = pin
            message.request_type = RequestMessage.SET
            message.value = True
            messageList.append(message)

        return messageList

    @staticmethod
    def getAll():
        messageList = []

        for pin in ["LLS_IN_GP_KL_01", "LLS_IN_GP_KL_02", "LLS_IN_GP_KL_03", "LLS_IN_GP_KL_04",
                    "PA_KLIN1", "PA_KLIN2", "PA_KLIN3", "PA_KLIN4", "PA_KLIN5", "PA_KLIN6", "PA_KLIN7",
                    "PA_KLIN8", "PA_MUTE"]:
            message = RequestMessage()
            message.pin_name = pin
            message.request_type = RequestMessage.GET
            messageList.append(message)
        return messageList

## IFEGPIO Unit Test
class Test_IFEGPIO(unittest.TestCase):
    ## Static logger instance
    log = None
    ## Static module instance
    module = None

    ## Setup for the Encoder test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test IFEGPIO')
        cls.log.info('++++ Setup before IFEGPIO module unit tests ++++')
        #  Create the module
        cls.module = gpio.IFEGPIO()
        #  Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Tests the functionality of the gpio module
    def test_All(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: All Set Messages and All Get Messages ****")
        log.info("==== Sending All Set Message ====")

        for message in IFEGPIOMessages.setAll():
            response = module.msgHandler(ThalesZMQMessage(message))
            self.assertEqual(response.name, "ResponseMessage")
            self.assertEqual(response.body.pin_name, message.pin_name)
            self.assertEqual(response.body.state, message.value)
            self.assertEqual(response.body.direction, OUTPUT)
            self.assertEqual(response.body.error, ResponseMessage.OK)

        log.info("==== Sending All Get Message ====")

        for message in IFEGPIOMessages.getAll():
            response = module.msgHandler(ThalesZMQMessage(message))
            self.assertEqual(response.name, "ResponseMessage")
            self.assertEqual(response.body.pin_name, message.pin_name)
            self.assertEqual(response.body.direction, INPUT)
            self.assertEqual(response.body.error, ResponseMessage.OK)

if __name__ == '__main__':
    unittest.main()

## @endcond
