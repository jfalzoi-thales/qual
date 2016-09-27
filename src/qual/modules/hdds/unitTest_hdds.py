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
        return [("Get all power supply values", HDDSMessages.getPSWC),
                ("Get GPIO pin", HDDSMessages.get),
                ("Get GPIO pins", HDDSMessages.getMul),
                ("Set GPIO pins", HDDSMessages.setMul),
                ("Get IFE temperature", HDDSMessages.getTemp),
                ("Get IFE voltage",     HDDSMessages.getVolt)]

    @staticmethod
    def getPSWC():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "power_supply.28V_monitor.*"
        return message

    @staticmethod
    def get():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "external_pins.output.pin_a_a13"
        return message

    @staticmethod
    def getMul():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "external_pins.input.pin_a_d13"
        value = message.values.add()
        value.key = "external_pins.input.pin_a_b14"
        value = message.values.add()
        value.key = "external_pins.input.pin_a_b13"
        value = message.values.add()
        value.key = "external_pins.input.pin_a_c15"
        value = message.values.add()
        value.key = "external_pins.input.pin_a_a15"
        return message

    @staticmethod
    def setMul():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "external_pins.output.pin_a_e15"
        value.value = "HIGH"
        value = message.values.add()
        value.key = "external_pins.output.pin_a_d14"
        value.value = "HIGH"
        value = message.values.add()
        value.key = "external_pins.output.pin_a_d15"
        value.value = "HIGH"
        value = message.values.add()
        value.key = "external_pins.output.pin_a_c14"
        value.value = "HIGH"
        value = message.values.add()
        value.key = "external_pins.output.pin_a_c13"
        value.value = "HIGH"
        return message

    @staticmethod
    def getTemp():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "ife.temperature.U15_TINT"
        return message

    @staticmethod
    def setTemp():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "ife.temperature.U15_TINT"
        value.value = "HIGH"
        return message

    @staticmethod
    def getVolt():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "ife.voltage.U130_3V3"
        return message

    @staticmethod
    def setVolt():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "ife.voltage.U130_3V3"
        value.value = "HIGH"
        return message

    @staticmethod
    def getBogus():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "bogus_key"
        return message

    @staticmethod
    def setBogus():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "bogus_key_1"
        value.value = "x"
        value = message.values.add()
        value.key = "bogus_key_2"
        value.value = "y"
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
        if cls.module is None:
            cls.module = hdds.HDDS()

    ## Test case: Use wildcards. Get "power_supply.28V_monitor.*"
    # Asserts:
    #       success == True
    #       key     == "power_supply.28V_monitor.*"
    #       value   != ""
    def test_getPSWC(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Test case: Get all Power Supply ****")
        # Dictionary with the expected responses
        expectedResponses = {"power_supply.28V_monitor.voltage":"28.375256",
                             "power_supply.28V_monitor.current":"1.845365",
                             "power_supply.28V_monitor.external_temperature":"38.375000",
                             "power_supply.28V_monitor.internal_temperature":"41.000000"}
        # Get the reponse
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.getPSWC()))
        # Iterate over all responses
        for propertyResponse in response.body.values:
            self.assertTrue(propertyResponse.success)
            self.assertTrue(propertyResponse.key in expectedResponses.keys())
            self.assertNotEqual(propertyResponse.value, "")
        log.info("==== Test complete ====")

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
        for propertyResponse in response.body.values:
            self.assertFalse(propertyResponse.success)
            self.assertEqual(propertyResponse.key, "bogus_key")
            self.assertEqual(propertyResponse.value, "")
        log.info("==== Test complete ====")

    ## Test case: Try to set an invalid keys
    # Asserts:
    #       success == False
    #       key     in ["bogus_key_1","bogus_key_2"]
    #       value   ==      "x"      ,      "y"
    def test_setInvalidKeys(self):
        log = self.__class__.log
        module = self.__class__.module
        # Dictionary with the expected responses
        expectedResponses = {"bogus_key_1":"x",
                             "bogus_key_2":"y",}
        log.info("**** Test case: Set invalid keys ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.setBogus()))
        for propertyResponse in response.body.values:
            self.assertFalse(propertyResponse.success)
            self.assertTrue(propertyResponse.key in expectedResponses.keys())
            self.assertEqual(propertyResponse.value, expectedResponses[propertyResponse.key])
        log.info("==== Test complete ====")

    ## Test case: Try to get a single value
    #  Asserts:
    #       success == True
    #       key     == "external_pins.output.pin_a6"
    #       value   != ""
    def test_getSingle(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get single ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.get()))
        for propertyResponse in response.body.values:
            self.assertEqual(propertyResponse.success, True)
            self.assertEqual(propertyResponse.key, "external_pins.output.pin_a_a13")
            self.assertNotEqual(propertyResponse.value, "")
        log.info("==== Test complete ====")

    ## Test case: Try to get a multiple values
    #  Asserts:
    #       success == True
    #       key     == [in list]
    #       value   != ""
    def test_getMultiple(self):
        log = self.__class__.log
        module = self.__class__.module
        keyList = ["external_pins.input.pin_a_d13",
                   "external_pins.input.pin_a_b14",
                   "external_pins.input.pin_a_b13",
                   "external_pins.input.pin_a_c15",
                   "external_pins.input.pin_a_a15"]

        log.info("**** Test case: Get multiple ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.getMul()))
        for propertyResponse in response.body.values:
            self.assertEqual(propertyResponse.success, True)
            self.assertTrue(propertyResponse.key in keyList)
            self.assertNotEqual(propertyResponse.value, "")
        log.info("==== Test complete ====")

    ## Test case: Try to set a multiple values
    #  Asserts:
    #       success == True
    #       key     == [in list]
    #       value   == "HIGH"
    def test_setMultiple(self):
        log = self.__class__.log
        module = self.__class__.module
        keyList = ["external_pins.output.pin_a_e15",
                   "external_pins.output.pin_a_d14",
                   "external_pins.output.pin_a_d15",
                   "external_pins.output.pin_a_c14",
                   "external_pins.output.pin_a_c13"]

        log.info("**** Test case: Set value ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.setMul()))
        for propertyResponse in response.body.values:
            self.assertEqual(propertyResponse.success, True)
            self.assertTrue(propertyResponse.key in keyList)
            self.assertEqual(propertyResponse.value, "HIGH")
        log.info("==== Test complete ====")

    ## Test case: Test get IFE temperature/voltage :
    #       success == True
    #       key     == [what was specified]
    #       value   != ""
    def test_getIFE(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get temp ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.getTemp()))
        for propertyResponse in response.body.values:
            self.assertTrue(propertyResponse.success)
            self.assertEqual(propertyResponse.key, "ife.temperature.U15_TINT")
            self.assertNotEqual(propertyResponse.value, "")

        log.info("**** Test case: Get volt ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.getVolt()))
        for propertyResponse in response.body.values:
            self.assertTrue(propertyResponse.success)
            self.assertEqual(propertyResponse.key, "ife.voltage.U130_3V3")
            self.assertNotEqual(propertyResponse.value, "")

        log.info("==== Test complete ====")

    ## Test case: Test set IFE temperature/voltage :
    #       success == False
    #       key     == [what was specified]
    #       value   == "HIGH"
    def test_setIFE(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Set temp ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.setTemp()))
        for propertyResponse in response.body.values:
            self.assertFalse(propertyResponse.success)
            self.assertEqual(propertyResponse.key, "ife.temperature.U15_TINT")
            self.assertEqual(propertyResponse.value, "HIGH")

        log.info("**** Test case: Set volt ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.setVolt()))
        for propertyResponse in response.body.values:
            self.assertFalse(propertyResponse.success)
            self.assertEqual(propertyResponse.key, "ife.voltage.U130_3V3")
            self.assertEqual(propertyResponse.value, "HIGH")

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond