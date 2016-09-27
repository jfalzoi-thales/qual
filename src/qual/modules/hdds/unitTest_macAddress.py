import unittest

import hdds
from qual.pb2.HDDS_pb2 import HostDomainDeviceServiceRequest
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


#  @cond doxygen_unittest

## MacAddress Messages
class MacAddressMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "MacAddress"

    @staticmethod
    def getMenuItems():
        return [("Get all MAC addresses",       MacAddressMessages.getAllMacs),]

    @staticmethod
    def getMacs(keyList=None):
        keys = keyList if keyList else ["mac_address.switch",
                                        "mac_address.processor",
                                        "mac_address.i350_1",
                                        "mac_address.i350_2",
                                        "mac_address.i350_3",
                                        "mac_address.i350_4"]
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET

        for key in keys:
            value = message.values.add()
            value.key = key

        return message

    @staticmethod
    def getAllMacs():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        value = message.values.add()
        value.key = "mac_address.*"
        return message

    @staticmethod
    def setMacs(valDict=None):
        values = valDict if valDict else {"mac_address.switch":     "00:40:00:00:00:00",
                                          "mac_address.processor":  "00:40:00:00:01:00",
                                          "mac_address.i350_1":     "00:40:00:00:02:00",
                                          "mac_address.i350_2":     "00:40:00:00:02:01",
                                          "mac_address.i350_3":     "00:40:00:00:02:02",
                                          "mac_address.i350_4":     "00:40:00:00:02:03"}
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
        value.key = "mac_address.bogus"
        return message

    @staticmethod
    def setBogusKey():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "mac_address.bogus"
        value.value = "00:11:22:33:44:55"
        return message

    @staticmethod
    def setBogusMac():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "mac_address.processor"
        value.value = "BO:GU:SS:TU:FF:SS"
        return message

    @staticmethod
    def setAllMacs():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.SET
        value = message.values.add()
        value.key = "mac_address.*"
        value.value = "00:40:00:00:00:00"
        return message


## MacAddress Unit Test
class Test_MacAddress(unittest.TestCase):
    ## Static logger instance
    log = None
    ## Static module instance
    module = None

    ## Setup for the MacAddress test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test MacAddress')
        cls.log.info('++++ Setup before MacAddress unit tests ++++')

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
    #  Get Original Macs,
    #  Set Test Macs,
    #  Get New Macs,
    #  Set Original Macs,
    #  Get Final Macs
    def test_MultipleKeys(self):
        log = self.__class__.log
        module = self.__class__.module
        origValDict = {}
        testValDict = {"mac_address.switch":     "00:40:00:00:00:00",
                       "mac_address.processor":  "00:40:00:00:01:00",
                       "mac_address.i350_1":     "00:40:00:00:02:00",
                       "mac_address.i350_2":     "00:40:00:00:02:01",
                       "mac_address.i350_3":     "00:40:00:00:02:02",
                       "mac_address.i350_4":     "00:40:00:00:02:03"}

        log.info("**** Test Multiple Keys: Get Original Macs, Set Test Macs, Get New Macs, Set Original Macs, Get Final Macs ****")
        log.info("==== Get Original Macs ====")
        response = module.msgHandler(ThalesZMQMessage(MacAddressMessages.getMacs()))

        for value in response.body.values:
            self.assertTrue(value.success)
            origValDict[value.key] = value.value

        log.info("==== Set Test Macs ====")
        response = module.msgHandler(ThalesZMQMessage(MacAddressMessages.setMacs(testValDict)))
        self.checkResp(response.body.values, testValDict)

        log.info("==== Set Original Macs ====")
        response = module.msgHandler(ThalesZMQMessage(MacAddressMessages.setMacs(origValDict)))
        self.checkResp(response.body.values, origValDict)

        log.info("==== Test Complete ====")

    ## Test Case:,
    #  Get All Macs
    def test_WildCardKey(self):
        log = self.__class__.log
        module = self.__class__.module
        macKeys = ["mac_address.switch",
                   "mac_address.processor",
                   "mac_address.i350_1",
                   "mac_address.i350_2",
                   "mac_address.i350_3",
                   "mac_address.i350_4"]

        log.info("**** Test Wild Cards: Get All Macs ****")
        log.info("==== Get All Macs ====")
        response = module.msgHandler(ThalesZMQMessage(MacAddressMessages.getAllMacs()))
        self.assertEqual(len(response.body.values), len(macKeys))

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.key in macKeys)

        log.info("==== Test Complete ====")

    ## Test Case:
    #  Get Bogus Key,
    #  Set Bogus Key,
    #  Set Bogus Mac,
    #  Set All Macs
    def test_FailureCases(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Test Failure Cases: Get Bogus Key, Set Bogus Key, Set Bogus Mac, Set All Macs ****")
        log.info("==== Get Bogus Key ====")
        response = module.msgHandler(ThalesZMQMessage(MacAddressMessages.getBogusKey()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "mac_address.bogus")
        self.assertFalse(response.body.values[0].value)

        log.info("==== Set Bogus Key ====")
        response = module.msgHandler(ThalesZMQMessage(MacAddressMessages.setBogusKey()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "mac_address.bogus")
        self.assertEqual(response.body.values[0].value, "00:11:22:33:44:55")

        log.info("==== Set Bogus Mac ====")
        response = module.msgHandler(ThalesZMQMessage(MacAddressMessages.setBogusMac()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "mac_address.processor")
        self.assertEqual(response.body.values[0].value, "BO:GU:SS:TU:FF:SS")

        log.info("==== Set All Macs ====")
        response = module.msgHandler(ThalesZMQMessage(MacAddressMessages.setAllMacs()))

        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].key, "mac_address.*")
        self.assertEqual(response.body.values[0].value, "00:40:00:00:00:00")

        log.info("==== Test Complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
