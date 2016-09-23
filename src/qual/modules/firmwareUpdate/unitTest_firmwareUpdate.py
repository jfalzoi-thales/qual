import unittest
import time

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
        return "FirmwareUpdate"

    @staticmethod
    def getMenuItems():
        return [("Update BIOS",                        FirmwareUpdateMessages.updateBIOS),
                ("Update BIOS and reboot",             FirmwareUpdateMessages.updateBIOSReboot),
                ("Update I350 EEPROM",                 FirmwareUpdateMessages.updateI350EEPROM),
                ("Update I350 Flash",                  FirmwareUpdateMessages.updateI350Flash),
                ("Update Switch Boot Loader",          FirmwareUpdateMessages.switchBootloader),
                ("Update Switch Firmware",             FirmwareUpdateMessages.switchFirmware),
                ("Switch Firmware Swap",               FirmwareUpdateMessages.switchFirmwareSwap),
                ("Update Switch Config",               FirmwareUpdateMessages.updateSwitchConfig),
                ("Switch Config Swap",                 FirmwareUpdateMessages.updateSwitchConfigSwap)]

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
    def switchBootloader():
        message = FirmwareUpdateRequest()
        message.command = FW_SWITCH_BOOTLOADER
        message.reboot = False
        return message

    @staticmethod
    def switchFirmware():
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
    def updateSwitchConfigSwap():
        message = FirmwareUpdateRequest()
        message.command = FW_SWITCH_CONFIG_SWAP
        message.reboot = False
        return message


## FirmwareUpdate Unit Test
class Test_FirmwareUpdate(unittest.TestCase):
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
        cls.log.info('++++ Setup before FirmwareUpdate module unit tests ++++')
        #  Create the module
        if cls.module is None:
            cls.module = firmwareUpdate.FirmwareUpdate()

    ## Teardown when done with test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after unit tests ++++")
        cls.module.terminate()

    ## Valid Test Case: Update BIOS firmware and update unimplemented device firmware
    #  Asserts:
    #       command   == FW_BIOS
    #       result    == FirmwareUpdateResponse.ALL_PASSED
    #       ---------------------
    #       command   == FW_I350
    #       result    == FirmwareUpdateResponse.ALL_FAILED
    #       ---------------------
    #       command   == FW_SWITCH_CONFIG
    #       success   == True
    #       ---------------------
    #       command   == FW_SWITCH_CONFIG_SWAP
    #       success   == True
    #       ---------------------
    def test_all(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Valid Test Case: Update BIOS Firmware ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateBIOS()))
        self.assertTrue(response.body.success)

        log.info("**** Valid Test Case: Update I350 EEPROM ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateI350EEPROM()))
        self.assertTrue(response.body.success)

        log.info("**** Valid Test Case: Update I350 Firmware ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateI350Flash()))
        self.assertTrue(response.body.success)

        # TODO: Uncomment below once we can securely upgrade and swap the switch firmware
        # log.info("**** Valid Test Case: Upgrade Switch Firmware ****")
        # response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.switchFirmware()))
        # self.assertTrue(response.body.success)
        #
        # log.info("**** Valid Test Case: Swap Switch Firmware ****")
        # response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.switchFirmwareSwap()))
        # self.assertTrue(response.body.success)

        log.info("**** Valid Test Case: Update Switch Configuration ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateSwitchConfig()))
        self.assertTrue(response.body.success)

        log.info("**** Valid Test Case: Update Switch Configuration Swap ****")
        response = module.msgHandler(ThalesZMQMessage(FirmwareUpdateMessages.updateSwitchConfigSwap()))
        self.assertTrue(response.body.success)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
