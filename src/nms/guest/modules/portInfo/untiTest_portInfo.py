import unittest

import portInfo
from nms.guest.pb2.nms_guest_api_pb2 import PortInfoReq
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


#  @cond doxygen_unittest

## PortInfo Messages
class PortInfoMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Port Info"

    @staticmethod
    def getMenuItems():
        return [("Get Single Key",          PortInfoMessages.getSingle),
                ("Get Multiple Keys",       PortInfoMessages.getMultiple),
                ("Get I350 VLANs",          PortInfoMessages.getI350Vlans),
                ("Get All Internal Speed",  PortInfoMessages.getAllIntSpeed),
                ("Get All Speed",           PortInfoMessages.getAllSpeed),
                ("Get All Internal Stats",  PortInfoMessages.getAllIntStats),
                ("Get All Stats",           PortInfoMessages.getAllStats),
                ("Get All Keys",            PortInfoMessages.getAll)]

    @staticmethod
    def getSingle():
        message = PortInfoReq()
        message.portInfoKey.append("external.enet_1.shutdown")
        return message

    @staticmethod
    def getSingleVlan():
        message = PortInfoReq()
        message.portInfoKey.append("external.enet_1.vlan_id")
        return message

    @staticmethod
    def getMultiple():
        message = PortInfoReq()
        message.portInfoKey.extend(["external.enet_8.shutdown", "internal.i350_1.shutdown"])
        return message

    @staticmethod
    def getI350Vlans():
        message = PortInfoReq()
        message.portInfoKey.extend(["internal.i350_1.vlan_id", "internal.i350_2.vlan_id", "internal.i350_3.vlan_id", "internal.i350_4.vlan_id"])
        return message

    @staticmethod
    def getAllSpeedSinglePort():
        message = PortInfoReq()
        message.portInfoKey.append("*.enet_1.speed")
        return message

    @staticmethod
    def getAllIntSpeed():
        message = PortInfoReq()
        message.portInfoKey.append("internal.*.speed")
        return message

    @staticmethod
    def getAllSpeed():
        message = PortInfoReq()
        message.portInfoKey.append("*.speed")
        return message

    @staticmethod
    def getAllIntStats():
        message = PortInfoReq()
        message.portInfoKey.append("internal.*")
        return message

    @staticmethod
    def getAllStats(ports=None):
        message = PortInfoReq()
        portList = ports if ports else ["external.ENET_1", "external.ENET_8", "internal.i350_1"]

        for port in portList:
            message.portInfoKey.append(port + ".*")

        return message

    @staticmethod
    def getAll():
        message = PortInfoReq()
        message.portInfoKey.append("*")
        return message

    @staticmethod
    def getEmpty():
        message = None
        return message

    @staticmethod
    def getBogus():
        message = PortInfoReq()
        message.portInfoKey.append("internal.BOGUS.speed")
        return message

## PortInfo Unit Test
class Test_PortInfo(unittest.TestCase):
    ## Static logger instance
    log = None
    ## Static module instance
    module = None

    ## Setup for the PortInfo test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test PortInfo')
        cls.log.info('++++ Setup before PortInfo module unit tests ++++')
        # Create the module
        if cls.module is None:
            cls.module = portInfo.PortInfo()

    ## Teardown when done with PortInfo test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after PortInfo module unit tests ++++")
        cls.module.terminate()

    ## Test Case: Get A Single Key
    def test_GetSingle(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test Case: Get A Single Key ****")

        response = module.msgHandler(ThalesZMQMessage(PortInfoMessages.getSingle()))

        self.assertEqual(response.name, "PortInfoResp")
        self.assertTrue(response.body.values[0].success)
        self.assertEqual(response.body.values[0].keyValue.key, "external.enet_1.shutdown")
        self.assertTrue(response.body.values[0].keyValue.value)

        log.info("==== Test Complete ====")

    ## Test Case: Get Multiple Keys
    def test_GetMultiple(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test Case: Get Multiple Keys ****")

        response = module.msgHandler(ThalesZMQMessage(PortInfoMessages.getMultiple()))

        self.assertEqual(response.name, "PortInfoResp")
        self.assertEqual(len(response.body.values), 2)

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.keyValue.key in ["external.enet_8.shutdown", "internal.i350_1.shutdown"])
            self.assertTrue(value.keyValue.value)

        log.info("==== Test Complete ====")

    ## Test Case: Get All Stats for All Ports
    def test_GetAll(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test Case: Get All Stats for All Ports ****")

        response = module.msgHandler(ThalesZMQMessage(PortInfoMessages.getAll()))

        self.assertEqual(response.name, "PortInfoResp")
        self.assertGreaterEqual(len(response.body.values), 280)

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.keyValue.key)
            self.assertTrue(value.keyValue.value)

        log.info("==== Test Complete ====")

    ## Test Case: Get All Speeds for Single Port
    def test_GetAllSpeedSinglePort(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test Case: Get All Speeds for Single Port ****")

        response = module.msgHandler(ThalesZMQMessage(PortInfoMessages.getAllSpeedSinglePort()))

        self.assertEqual(response.name, "PortInfoResp")
        self.assertEqual(len(response.body.values), 1)

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.keyValue.key.endswith("speed"))
            self.assertTrue(value.keyValue.value)

        log.info("==== Test Complete ====")

    ## Test Case: Get All Internal Speeds
    def test_GetAllIntSpeed(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test Case: Get All Internal Speeds ****")

        response = module.msgHandler(ThalesZMQMessage(PortInfoMessages.getAllIntSpeed()))

        self.assertEqual(response.name, "PortInfoResp")
        self.assertEqual(len(response.body.values), 24)

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.keyValue.key.startswith("internal"))
            self.assertTrue(value.keyValue.key.endswith("speed"))
            self.assertTrue(value.keyValue.value)

        log.info("==== Test Complete ====")

    ## Test Case: Get All Speeds for All Ports
    def test_GetAllSpeed(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test Case: Get All Speeds for All Ports ****")

        response = module.msgHandler(ThalesZMQMessage(PortInfoMessages.getAllSpeed()))

        self.assertEqual(response.name, "PortInfoResp")
        self.assertEqual(len(response.body.values), 40)

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.keyValue.key.endswith("speed"))
            self.assertTrue(value.keyValue.value)

        log.info("==== Test Complete ====")

    ## Test Case: Get All Internal Stats
    def test_GetAllIntStats(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test Case: Get All Internal Stats ****")

        response = module.msgHandler(ThalesZMQMessage(PortInfoMessages.getAllIntStats()))

        self.assertEqual(response.name, "PortInfoResp")
        self.assertGreaterEqual(len(response.body.values), 168)

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.keyValue.key.startswith("internal"))
            self.assertTrue(value.keyValue.value)

        log.info("==== Test Complete ====")

    ## Test Case: Get All Stats for the Different Port Types (Switch, CPU, and i350 Card)
    def test_GetAllStats(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test Case: Get All Stats for the Different Port Types (Switch, CPU, and i350 Card) ****")

        response = module.msgHandler(ThalesZMQMessage(PortInfoMessages.getAllStats()))

        self.assertEqual(response.name, "PortInfoResp")
        self.assertGreaterEqual(len(response.body.values), 21)

        for value in response.body.values:
            self.assertTrue(value.success)
            self.assertTrue(value.keyValue.key.startswith(("external.ENET_1", "external.ENET_8", "internal.i350_1")))
            self.assertTrue(value.keyValue.value)

        log.info("==== Test Complete ====")

    ## Test Case: Get Bogus Key
    def test_GetBogus(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test Case: Get Bogus Key ****")

        response = module.msgHandler(ThalesZMQMessage(PortInfoMessages.getBogus()))

        self.assertEqual(response.name, "PortInfoResp")
        self.assertFalse(response.body.values[0].success)
        self.assertEqual(response.body.values[0].keyValue.key, "internal.BOGUS.speed")
        self.assertFalse(response.body.values[0].keyValue.value)
        self.assertEqual(response.body.values[0].error.error_code, 1003)
        self.assertEqual(response.body.values[0].error.error_description, "Port name does not exist in this setup")

        log.info("==== Test Complete ====")

    ## Test Case: Get a Vlan_id
    def test_GetSingleVlan(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test Case: Get a Vlan_id ****")

        response = module.msgHandler(ThalesZMQMessage(PortInfoMessages.getSingleVlan()))

        self.assertEqual(response.name, "PortInfoResp")
        self.assertTrue(response.body.values[0].success)
        self.assertEqual(response.body.values[0].keyValue.key, 'external.enet_1.vlan_id')
        self.assertTrue(response.body.values[0].keyValue.value)

        log.info("==== Test Complete ====")


if __name__ == '__main__':
    unittest.main()

## @endcond
