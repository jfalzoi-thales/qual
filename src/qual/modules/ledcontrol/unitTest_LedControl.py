import unittest

from led import Led
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.pb2.LED_pb2 import *


# @cond doxygen_unittest

## LED Control Messages
class LedControlMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "LED Control"

    @staticmethod
    def getMenuItems():
        return [("(ON, LED_POST)",        LedControlMessages.onPost),
                ("(ON, STATUS_GREEN)",  LedControlMessages.onTestGreen),
                ("(ON, STATUS_YELLOW)", LedControlMessages.onTestYellow),
                ("(OFF,LED_POST)",        LedControlMessages.offPost),
                ("(OFF,STATUS_GREEN)",  LedControlMessages.offTestGreen),
                ("(OFF,STATUS_YELLOW)", LedControlMessages.offTestYellow)]

    @staticmethod
    def onPost():
        message = LEDRequest()
        message.led   = LED_POST
        message.state = LS_ON
        return message

    @staticmethod
    def onTestGreen():
        message = LEDRequest()
        message.led   = LED_STATUS_GREEN
        message.state = LS_ON
        return message

    @staticmethod
    def onTestYellow():
        message = LEDRequest()
        message.led   = LED_STATUS_YELLOW
        message.state = LS_ON
        return message
    @staticmethod
    def offPost():
        message = LEDRequest()
        message.led   = LED_POST
        message.state = LS_OFF
        return message

    @staticmethod
    def offTestGreen():
        message = LEDRequest()
        message.led   = LED_STATUS_GREEN
        message.state = LS_OFF
        return message

    @staticmethod
    def offTestYellow():
        message = LEDRequest()
        message.led   = LED_STATUS_YELLOW
        message.state = LS_OFF
        return message

## LED Control Unit Test
class Test_LedControl(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the LED Control test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='LED Control')
        cls.log.info('++++ Setup before LED Control module unit tests ++++')
        # Create the module
        if cls.module is None:
            cls.module = Led()

    ## Teardown when done with LED Control test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after LED Control module unit tests ++++")
        cls.module.terminate()

    ## Valid Test case:
    #
    def test_OnPost(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: ON, LED_POST message ****")
        response = module.msgHandler(ThalesZMQMessage(LedControlMessages.onPost()))
        # Asserts
        self.assertEqual(response.name, "LEDResponse")
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

    ## Valid Test case:
    #
    def test_OnGreen(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: ON, LED_STATUS_GREEN message ****")
        response = module.msgHandler(ThalesZMQMessage(LedControlMessages.onTestGreen()))
        # Asserts
        self.assertEqual(response.name, "LEDResponse")
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

    ## Valid Test case:
    #
    def test_OnYellow(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: ON, LED_STATUS_YELLOW message ****")
        response = module.msgHandler(ThalesZMQMessage(LedControlMessages.onTestYellow()))
        # Asserts
        self.assertEqual(response.name, "LEDResponse")
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

    ## Valid Test case:
    #
    def test_OffPost(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: OFF, LED_POST message ****")
        response = module.msgHandler(ThalesZMQMessage(LedControlMessages.offPost()))
        # Asserts
        self.assertEqual(response.name, "LEDResponse")
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

    ## Valid Test case:
    #
    def test_OffGreen(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: OFF, LED_STATUS_GREEN message ****")
        response = module.msgHandler(ThalesZMQMessage(LedControlMessages.offTestGreen()))
        # Asserts
        self.assertEqual(response.name, "LEDResponse")
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

    ## Valid Test case:
    #
    def test_OffYellow(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: OFF, LED_STATUS_YELLOW message ****")
        response = module.msgHandler(ThalesZMQMessage(LedControlMessages.offTestYellow()))
        # Asserts
        self.assertEqual(response.name, "LEDResponse")
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
