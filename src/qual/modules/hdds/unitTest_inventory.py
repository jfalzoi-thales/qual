import unittest

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
                ("Get bogus key",                   InventoryMessages.getBogusKey),
                ("Set both types of valid keys",    InventoryMessages.setKeys),
                ("Set all LRU keys",                InventoryMessages.setAllLRUKeys),
                ("Set all keys",                    InventoryMessages.setAllKeys),
                ("Set bogus key",                   InventoryMessages.setBogusKey)]

    @staticmethod
    def getKeys(keyList=None):
        keys = keyList if keyList else ["inventory.lru.serial_number", "inventory.carrier_card.serial_number"]
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
    def getBogusKey():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "inventory.bogus"
        return message

    @staticmethod
    def setKeys(valDict=None):
        values = valDict if valDict else {"inventory.lru.serial_number":            "MULTIPLE KEYS",
                                          "inventory.carrier_card.serial_number":   "MULTIPLE KEYS CC"}
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET

        for key in values:
            value = message.values.add()
            value.key = key
            value.value = values[key]

        return message

    @staticmethod
    def setAllLRUKeys(val="ALL LRU KEYS"):
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "inventory.lru.*"
        value.value = val
        return message

    @staticmethod
    def setAllKeys(val="ALL KEYS"):
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "inventory.*"
        value.value = val
        return message

    @staticmethod
    def setBogusKey(val="BOGUS"):
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "inventory.bogus"
        value.value = val
        return message

## Inventory Unit Test
class Test_Inventory(unittest.TestCase):
    ## Static logger instance
    log = None
    ## Static module instance
    module = None

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
    #  Get original values,
    #  Set test values,
    #  Get test values,
    #  Set original values,
    #  Get original values
    def test_MultipleKeys(self):
        log = self.__class__.log
        module = self.__class__.module
        origValDict = {}
        testValDict = {"inventory.lru.serial_number": "MULTIPLE KEYS",
                       "inventory.carrier_card.serial_number": "MULTIPLE KEYS CC"}

        log.info("**** Test Multiple Keys: Get original values, Set test values, Get test values, Set original values, Get original values ****")
        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getKeys()))

        for value in response.body.values:
            self.assertTrue(value.success)
            origValDict[value.key] = value.value

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.setKeys()))
        self.checkResp(response.body.values, testValDict)

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getKeys()))
        self.checkResp(response.body.values, testValDict)

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.setKeys(origValDict)))
        self.checkResp(response.body.values, origValDict)

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getKeys(origValDict.keys())))
        self.checkResp(response.body.values, origValDict)

        log.info("==== Test Complete ====")

    ## Test Case:
    #  Get all LRU keys,
    #  Get all keys
    def test_WildCardKeys(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Test Wild Cards: Get all LRU keys, Get all keys ****")

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getAllLRUKeys()))

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.key.startswith("inventory.lru"))

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getAllKeys()))

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.key.startswith("inventory"))

        log.info("==== Test Complete ====")

    ## Test Case:
    #  Set bogus key,
    #  Get bogus key,
    #  Set all LRU keys,
    #  Set all keys
    def test_FailureCases(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Test Failure Cases: Set bogus key, Get bogus key, Set all LRU keys, Set all keys ****")

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.setBogusKey()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "inventory.bogus")
        self.assertEqual(response.body.values[0].value, "BOGUS")

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.getBogusKey()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "inventory.bogus")
        self.assertFalse(response.body.values[0].value)

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.setAllLRUKeys()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "inventory.lru.*")
        self.assertEqual(response.body.values[0].value, "ALL LRU KEYS")

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.setAllKeys()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "inventory.*")
        self.assertEqual(response.body.values[0].value, "ALL KEYS")

        log.info("==== Test Complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
