import unittest

import firmwareUpdate
from qual.pb2.FirmwareUpdate_pb2 import *
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage

#  @cond doxygen_unittest

## Firmware Update Messages
class FirmwareUpdateMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Firmware Update"

    @staticmethod
    def getMenuItems():
        return [("Update BIOS",                        FirmwareUpdateMessages.updateBIOS),
                ("Update BIOS and reboot",             FirmwareUpdateMessages.updateBIOSReboot),
                ("Update I350 EEPROM",                 FirmwareUpdateMessages.updateI350EEPROM),
                ("Update I350 Flash",                  FirmwareUpdateMessages.updateI350Flash),
                ("Update Switch Bootloader",           FirmwareUpdateMessages.updateSwitchBootloader),
                ("Update Switch Firmware",             FirmwareUpdateMessages.updateSwitchFirmware),
                ("Switch Firmware Swap",               FirmwareUpdateMessages.switchFirmwareSwap),
                ("Update Switch Config",               FirmwareUpdateMessages.updateSwitchConfig),
                ("Switch Config Swap",                 FirmwareUpdateMessages.switchConfigSwap)]

    @staticmethod
    def updateBIOS():
        message = FirmwareUpdateRequest()
        message.command = FW_BIOS
        message.reboot = False
        return message

    @staticmethod
    def updateBIOSReboot():
        message = FirmwareUpdateRequest()
        message.command = FW_BIOS
        message.reboot = True
        return message

    @staticmethod
    def updateI350EEPROM():
        message = FirmwareUpdateRequest()
        message.command = FW_I350_EEPROM
        message.reboot = False
        return message

    @staticmethod
    def updateI350Flash():
        message = FirmwareUpdateRequest()
        message.command = FW_I350_FLASH
        message.reboot = False
        return message

    @staticmethod
    def updateSwitchBootloader():
        message = FirmwareUpdateRequest()
        message.command = FW_SWITCH_BOOTLOADER
        message.reboot = False
        return message

    @staticmethod
    def updateSwitchFirmware():
        message = FirmwareUpdateRequest()
        message.command = FW_SWITCH_FIRMWARE
        message.reboot = False
        return message

    @staticmethod
    def switchFirmwareSwap():
        message = FirmwareUpdateRequest()
        message.command = FW_SWITCH_FIRMWARE_SWAP
        message.reboot = False
        return message

    @staticmethod
    def updateSwitchConfig():
        message = FirmwareUpdateRequest()
        message.command = FW_SWITCH_CONFIG
        message.reboot = False
        return message

    @staticmethod
    def switchConfigSwap():
        message = FirmwareUpdateRequest()
        message.command = FW_SWITCH_CONFIG_SWAP
        message.reboot = False
        return message


## FirmwareUpdate Unit Test
class Test_FirmwareUpdate_BIOS(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the FirmwareUpdate test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test FirmwareUpdate')
        #  Create the module
        if cls.module is None:
            cls.module = firmwareUpdate.FirmwareUpdate()

    ## Teardown when done with test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.module.terminate()

    ## Valid Test Case: Update BIOS firmware
    def test_BIOS(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Update BIOS Firmware ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateBIOS()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")


## FirmwareUpdate Unit Test for I350 EEPROM
class Test_FirmwareUpdate_I350EEPROM(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the FirmwareUpdate test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test FirmwareUpdate')
        #  Create the module
        if cls.module is None:
            cls.module = firmwareUpdate.FirmwareUpdate()

    ## Teardown when done with test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.module.terminate()

    ## Valid Test Case: Update I350 EEPROM
    def test_I350EEPROM(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Update I350 EEPROM ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateI350EEPROM()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")


## FirmwareUpdate Unit Test for I350 Flash
class Test_FirmwareUpdate_I350Flash(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the FirmwareUpdate test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test FirmwareUpdate')
        #  Create the module
        if cls.module is None:
            cls.module = firmwareUpdate.FirmwareUpdate()

    ## Teardown when done with test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.module.terminate()

    ## Valid Test Case: Update I350 Flash
    def test_I350Flash(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Update I350 Flash ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateI350Flash()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")


## FirmwareUpdate Unit Test for Switch Bootloader
class Test_FirmwareUpdate_SwitchBootloader(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the FirmwareUpdate test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test FirmwareUpdate')
        #  Create the module
        if cls.module is None:
            cls.module = firmwareUpdate.FirmwareUpdate()

    ## Teardown when done with test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.module.terminate()

    ## Valid Test Case: Update Switch Bootloader
    def test_SwitchBootloader(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Update Switch Bootloader ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateSwitchBootloader()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")


## FirmwareUpdate Unit Test for Switch Firmware
class Test_FirmwareUpdate_SwitchFirmware(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the FirmwareUpdate test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test FirmwareUpdate')
        #  Create the module
        if cls.module is None:
            cls.module = firmwareUpdate.FirmwareUpdate()

    ## Teardown when done with test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.module.terminate()

    ## Valid Test Case: Update Switch Firmware
    def test_SwitchFirmware(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Update Switch Firmware ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateSwitchFirmware()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")


## FirmwareUpdate Unit Test for Switch Firmware Swap
class Test_FirmwareUpdate_SwitchFirmwareSwap(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the FirmwareUpdate test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test FirmwareUpdate')
        #  Create the module
        if cls.module is None:
            cls.module = firmwareUpdate.FirmwareUpdate()

    ## Teardown when done with test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.module.terminate()

    ## Valid Test Case: Switch Firmware Swap
    def test_SwitchFirmwareSwap(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Switch Firmware Swap ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.switchFirmwareSwap()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")


## FirmwareUpdate Unit Test for Switch Configuration
class Test_FirmwareUpdate_SwitchConfiguration(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the FirmwareUpdate test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test FirmwareUpdate')
        #  Create the module
        if cls.module is None:
            cls.module = firmwareUpdate.FirmwareUpdate()

    ## Teardown when done with test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.module.terminate()

    ## Valid Test Case: Update Switch Configuration
    def test_SwitchConfiguration(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Update Switch Configuration ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateSwitchConfig()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")


## FirmwareUpdate Unit Test for Switch Configuration Swap
class Test_FirmwareUpdate_SwitchConfigurationSwap(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the FirmwareUpdate test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test FirmwareUpdate')
        #  Create the module
        if cls.module is None:
            cls.module = firmwareUpdate.FirmwareUpdate()

    ## Teardown when done with test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.module.terminate()

    ## Valid Test Case: Switch Configuration Swap
    def test_SwitchConfigurationSwap(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("**** Valid Test Case: Switch Configuration Swap ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.switchConfigSwap()))
        self.assertTrue(response.body.success)
        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
