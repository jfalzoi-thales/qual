import unittest

import upgrade
from nms.host.pb2.nms_host_api_pb2 import UpgradeReq, I350, SWITCH, UPGRADE_FAILED, INVALID_UPGRADE_PACKAGE_PROVIDED, INVALID_NAME
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage

#  @cond doxygen_unittest

## Upgrade Messages
class UpgradeMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Upgrade"

    @staticmethod
    def getMenuItems():
        return [("Upgrade I350 EEPROM",                 UpgradeMessages.upgradeI350EEPROM),
                ("Upgrade I350 Flash",                  UpgradeMessages.upgradeI350Flash),
                ("Update Config",                       UpgradeMessages.uppdateConfig),
                ("Upgrade Switch",                      UpgradeMessages.upgradeSwitch)]

    @staticmethod
    def upgradeI350EEPROM():
        message = UpgradeReq()
        message.target = I350
        message.path = "/tmp/I350/firmware.txt"
        return message

    @staticmethod
    def upgradeI350Flash():
        message = UpgradeReq()
        message.target = I350
        message.path = "/tmp/I350/firmware"
        return message

    @staticmethod
    def upgradeSwitch():
        message = UpgradeReq()
        message.target = SWITCH
        message.path = "/tmp/Switch/firmware.dat"
        return message

    @staticmethod
    def uppdateConfig():
        message = UpgradeReq()
        message.target = SWITCH
        message.path = "/tmp/Switch/startup-config"
        return message

## Upgrade Unit Test for I350 EEPROM
class Test_Upgrade(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the Upgrade test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("nms")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test Upgrade')
        #  Create the module
        if cls.module is None:
            cls.module = upgrade.Upgrade()

    ## Teardown when done with test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.module.terminate()

    ## Valid Test Case: Upgrade I350 EEPROM
    def test_I350EEPROM(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Upgrade I350 EEPROM ****")
        response = module.msgHandler(ThalesZMQMessage(UpgradeMessages.upgradeI350EEPROM()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

    ## Valid Test Case: Upgrade I350 Flash
    def test_I350Flash(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Update I350 Flash ****")
        response = module.msgHandler(ThalesZMQMessage(UpgradeMessages.upgradeI350Flash()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

    ## Valid Test Case: Upgrade Switch
    def test_Switch(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Upgrade Switch ****")
        response = module.msgHandler(ThalesZMQMessage(UpgradeMessages.upgradeSwitch()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

    ## Valid Test Case: Update Switch config
    def test_SwitchConfig(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Update Switch Configuration ****")
        response = module.msgHandler(ThalesZMQMessage(UpgradeMessages.uppdateConfig()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
