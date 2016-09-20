import unittest

import hdds
from qual.pb2.HDDS_pb2 import HostDomainDeviceServiceRequest
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


#  @cond doxygen_unittest

## HDDS Messages
class HDDSMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "HDDS"

    @staticmethod
    def getMenuItems():
        return [("Get power supply value", HDDSMessages.getPS),
                ("Get GPIO pin", HDDSMessages.get),
                ("Set GPIO pin", HDDSMessages.set),
                ("Get IFE temperature", HDDSMessages.getTemp),
                ("Get IFE voltage",     HDDSMessages.getVolt)]

    @staticmethod
    def getPS():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        message.key = "power_supply.28V_monitor.current"
        return message

    @staticmethod
    def get():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        message.key = "external_pins.output.pin_a_a13"
        return message

    @staticmethod
    def set():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        message.key = "external_pins.output.pin_a_a13"
        message.value = "HIGH"
        return message

    @staticmethod
    def getTemp():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        message.key = "ife.temperature.U15_TINT"
        return message

    @staticmethod
    def setTemp():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        message.key = "ife.temperature.U15_TINT"
        message.value = "HIGH"
        return message

    @staticmethod
    def getVolt():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        message.key = "ife.voltage.U130_3V3"
        return message

    @staticmethod
    def setVolt():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        message.key = "ife.voltage.U130_3V3"
        message.value = "HIGH"
        return message

    @staticmethod
    def getBogus():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        message.key = "bogus_key"
        return message

    @staticmethod
    def setBogus():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        message.key = "bogus_key"
        message.value = "x"
        return message

## HDDS Unit Test
class Test_HDDS(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the HDDS test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test HDDS')
        cls.log.info('++++ Setup before HDDS module unit tests ++++')
        # Create the module
        cls.module = hdds.HDDS()
        # Uncomment this if you want to see module debug messages
        #cls.module.log.setLevel("DEBUG")

    ## Test case: Try to get an invalid key
    # Asserts:
    #       success == False
    #       key     == "bogus_key"
    #       value   == ""
    def test_getInvalidKey(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get invalid key ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.getBogus()))
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.key, "bogus_key")
        self.assertEqual(response.body.value, "")
        log.info("==== Test complete ====")

    ## Test case: Try to set an invalid key
    # Asserts:
    #       success == False
    #       key     == "bogus_key"
    #       value   == ""
    def test_setInvalidKey(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Set invalid key ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.setBogus()))
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.key, "bogus_key")
        self.assertEqual(response.body.value, "")
        log.info("==== Test complete ====")

    ## Test case: Try to get a single value# Asserts:
    #       success == True
    #       key     == "external_pins.output.pin_a6"
    #       value   != ""
    def test_get(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get single ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.get()))
        self.assertEqual(response.body.success, True)
        self.assertEqual(response.body.key, "external_pins.output.pin_a6")
        self.assertNotEqual(response.body.value, "")
        log.info("==== Test complete ====")

    ## Test case: Try to set a single value# Asserts:
    #       success == True
    #       key     == "external_pins.output.pin_a6"
    #       value   == "HIGH"
    def test_set(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Set value ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.set()))
        self.assertEqual(response.body.success, True)
        self.assertEqual(response.body.key, "external_pins.output.pin_a6")
        self.assertEqual(response.body.value, "HIGH")
        log.info("==== Test complete ====")

    ## Test case: Test temperature key requests:
    #       success == True
    #       key     == "external_pins.output.pin_a6"
    #       value   == "HIGH"
    def test_temp(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Set temp****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.setTemp()))
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.key, "ife.temperature.U15_TINT")
        self.assertEqual(response.body.value, "")

        log.info("**** Test case: Get temp****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.getTemp()))
        self.assertEqual(response.body.success, True)
        self.assertEqual(response.body.key, "ife.temperature.U15_TINT")
        self.assertNotEqual(response.body.value, "")

        log.info("==== Test complete ====")

    def test_volt(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Set volt****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.setVolt()))
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.key, "ife.voltage.U130_3V3")
        self.assertEqual(response.body.value, "")

        log.info("**** Test case: Get volt****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.getVolt()))
        self.assertEqual(response.body.success, True)
        self.assertEqual(response.body.key, "ife.voltage.U130_3V3")
        self.assertNotEqual(response.body.value, "")

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond