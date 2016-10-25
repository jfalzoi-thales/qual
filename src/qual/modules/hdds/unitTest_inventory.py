import unittest
from ConfigParser import SafeConfigParser

import hdds
from qual.pb2.HDDS_pb2 import HostDomainDeviceServiceRequest
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


#  @cond doxygen_unittest

## Inventory Messages
class InventoryMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Inventory"

    @staticmethod
    def getMenuItems():
        return [("Get both types of valid keys",    InventoryMessages.getKeys),
                ("Get all LRU keys",                InventoryMessages.getAllLRUKeys),
                ("Get all keys",                    InventoryMessages.getAllKeys),
                ("Set both types of valid keys",    InventoryMessages.setKeys)]

    @staticmethod
    def getKeys(keyList=None):
        keys = keyList if keyList else ["inventory.carrier_card.serial_number",
                                        "inventory.lru.serial_number",
                                        "inventory.ife.serial_number",
                                        "inventory.power_supply.serial_number",
                                        "inventory.processor_module.serial_number",
                                        "inventory.arinc_board.serial_number",
                                        "inventory.midplane.serial_number"]
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET

        for key in keys:
            value = message.values.add()
            value.key = key

        return message

    @staticmethod
    def getAllLRUKeys():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "inventory.lru.*"
        return message

    @staticmethod
    def getAllKeys():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "inventory.*"
        return message

    @staticmethod
    def setKeys(valDict=None):
        values = valDict if valDict else {"inventory.carrier_card.serial_number":       "CARRIER_CARD",
                                          "inventory.lru.serial_number":                "LRU",
                                          "inventory.ife.serial_number":                "IFE",
                                          "inventory.power_supply.serial_number":       "POWER_SUPPLY",
                                          "inventory.processor_module.serial_number":   "PROCESSOR_MODULE",
                                          "inventory.arinc_board.serial_number":        "ARINC_BOARD",
                                          "inventory.midplane.serial_number":           "MIDPLANE"}
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET

        for key in values:
            value = message.values.add()
            value.key = key
            value.value = values[key]

        return message

    @staticmethod
    def getBogusKey():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "inventory.bogus"
        return message

    @staticmethod
    def setBogusKey():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "inventory.bogus"
        value.value = "BOGUS"
        return message

    @staticmethod
    def setAllLRUKeys():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "inventory.lru.*"
        value.value = "ALL LRU KEYS"
        return message

    @staticmethod
    def setAllKeys():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "inventory.*"
        value.value = "ALL KEYS"
        return message

## Inventory Unit Test
class Test_Inventory(unittest.TestCase):
    ## Static logger instance
    log = None
    ## Static module instance
    module = None
    ## Static list of keys
    inventoryKeys = []

    ## Setup for the Inventory test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test Inventory')
        cls.log.info('++++ Setup before Inventory unit tests ++++')

        #  Create the module
        if cls.module is None:
            cls.module = hdds.HDDS()

        #  Parse key names from Thales Host Domain Device Service configuration file
        thalesHDDSConfig = "/thales/host/config/HDDS.conv"
        configParser = SafeConfigParser()
        configParser.read(thalesHDDSConfig)

        if configParser.sections() != []:
            cls.inventoryKeys = [option for option in configParser.options("hdds_host_convertions") if
                             option.startswith("inventory")]
        else:
            cls.log.warning("Missing or Empty Configuration File: %s" % thalesHDDSConfig)

    ## Check response value against expected values
    #  @param   self
    #  @param   values      values returned in the response
    #  @param   valDict     dictionary of expected keys and values
    def checkResp(self, values, valDict):
        for value in values:
            self.assertTrue(value.success)
            self.assertTrue(value.key in valDict)
            self.assertEqual(value.value, valDict[value.key])

    ## Test Case:
    #  Get Original Values,
    #  Set Test Values,
    #  Get New Values,
    #  Set Original Values,
    #  Get Final Values
    def test_MultipleKeys(self):
        log = self.__class__.log
        module = self.__class__.module
        inventoryKeys = self.__class__.inventoryKeys
        origValDict = {}
        testValDict = {"inventory.carrier_card.serial_number":       "CARRIER_CARD",
                       "inventory.lru.serial_number":                "LRU",
                       "inventory.ife.serial_number":                "IFE",
                       "inventory.power_supply.serial_number":       "POWER_SUPPLY",
                       "inventory.processor_module.serial_number":   "PROCESSOR_MODULE",
                       "inventory.arinc_board.serial_number":        "ARINC_BOARD",
                       "inventory.midplane.serial_number":           "MIDPLANE"}

        log.info("**** Test Multiple Keys: Get Original Values, Set Test Values, Get New Values, Set Original Values, Get Final Values ****")

        log.info("==== Check Serial Number Keys ====")
        #  Assert that all serial_number keys are in config file
        for key in testValDict: self.assertTrue(key in inventoryKeys)

        log.info("==== Get Original Values ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getKeys()))

        for value in response.body.values:
            self.assertTrue(value.success)
            origValDict[value.key] = value.value

        log.info("==== Set Test Values ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.setKeys()))
        self.checkResp(response.body.values, testValDict)

        log.info("==== Get New Values ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getKeys()))
        self.checkResp(response.body.values, testValDict)

        log.info("==== Set Original Values ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.setKeys(origValDict)))
        self.checkResp(response.body.values, origValDict)

        log.info("==== Get Final Values ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getKeys(origValDict.keys())))
        self.checkResp(response.body.values, origValDict)

        log.info("==== Test Complete ====")

    ## Test Case:
    #  Get All LRU Keys,
    #  Get All Keys
    def test_WildCardKeys(self):
        log = self.__class__.log
        module = self.__class__.module
        inventoryKeys = self.__class__.inventoryKeys
        lruKeys = [key for key in inventoryKeys if key.startswith("inventory.lru")]

        log.info("**** Test Wild Cards: Get All LRU Keys, Get All Keys ****")
        log.info("==== Get All LRU Keys ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getAllLRUKeys()))
        self.assertEqual(len(response.body.values), len(lruKeys))

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.key.startswith("inventory.lru"))
            self.assertTrue(value.key in lruKeys)

        log.info("==== Get All Keys ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getAllKeys()))
        self.assertEqual(len(response.body.values), len(inventoryKeys))

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.key.startswith("inventory"))
            self.assertTrue(value.key in inventoryKeys)

        log.info("==== Test Complete ====")

    ## Test Case:
    #  Set Bogus Key,
    #  Get Bogus Key,
    #  Set All LRU Keys,
    #  Set All Keys
    def test_FailureCases(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Test Failure Cases: Set Bogus Key, Get Bogus Key, Set All LRU Keys, Set All Keys ****")
        log.info("==== Set Bogus Key ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.setBogusKey()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "inventory.bogus")
        self.assertEqual(response.body.values[0].value, "BOGUS")

        log.info("==== Get Bogus Key ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getBogusKey()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "inventory.bogus")
        self.assertFalse(response.body.values[0].value)

        log.info("==== Set All LRU Keys ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.setAllLRUKeys()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "inventory.lru.*")
        self.assertEqual(response.body.values[0].value, "ALL LRU KEYS")

        log.info("==== Set All Keys ====")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.setAllKeys()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "inventory.*")
        self.assertEqual(response.body.values[0].value, "ALL KEYS")

        log.info("==== Test Complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
