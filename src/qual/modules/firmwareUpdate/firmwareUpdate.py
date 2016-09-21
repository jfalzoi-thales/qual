from time import sleep
from Queue import Queue
from subprocess import call

from qual.pb2.FirmwareUpdate_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage

## FirmwareUpdate Module
class FirmwareUpdate(Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config = None):
        super(FirmwareUpdate, self).__init__(config)
        ## Dict for storing Firmware Commands and their handlers
        self.firmFuncs = {FW_BIOS:                  self.updateBIOS,
                          FW_I350_EEPROM:           self.updateI350EEPROM,
                          FW_I350_FLASH:            self.updateI350Flash,
                          FW_SWITCH_BOOTLOADER:     self.unimplemented,
                          FW_SWITCH_FIRMWARE:       self.unimplemented,
                          FW_SWITCH_FIRMWARE_SWAP:  self.unimplemented,
                          FW_SWITCH_CONFIG:         self.unimplemented,
                          FW_SWITCH_CONFIG_SWAP:    self.unimplemented}
        ## Location of firmware images
        self.firmPath = "/thales/qual/firmware"
        ## Queue for storing a reboot request
        self.reboot = Queue()
        #  Adds handler to available message handlers
        self.addMsgHandler(FirmwareUpdateRequest, self.handler)
        #  Add thread for handling return messages before a reboot
        self.addThread(self.rebooter)

    ## Handles incoming tzmq messages
    #  @param     self
    #  @param     msg   tzmq format message
    #  @return    ThalesZMQMessage object
    def handler(self, msg):
        response = FirmwareUpdateResponse()

        if msg.body.command in self.firmFuncs:
            self.firmFuncs[msg.body.command](response, msg.body.reboot)
        else:
            response.success = False
            response.errorMessage = "Unexpected Command %s" % msg.body.command
            self.log.error("Unexpected Command %s" % msg.body.command)

        return ThalesZMQMessage(response)

    ## Attempts to upgrade the BIOS firmware using image included with QUAL
    #  @param   self
    #  @param   response    FirmwareUpdateResponse object
    #  @param   reboot      Reboot flag
    def updateBIOS(self, response, reboot):
        primary = False
        secondary = False

        # TODO: Check that we are running on an MPS before calling tools that modify firmware
        if call(["mps-biostool", "set-active", "primary"]) == 0:
            if call(["mps-biostool", "program-from", "%s/BIOS.firmware" % self.firmPath]) == 0:
                primary = True
            else:
                self.log.error("Unable to properly program primary BIOS.")
        else:
            self.log.error("Unable to set primary BIOS to active.")

        if call(["mps-biostool", "set-active", "secondary"]) == 0:
            if call(["mps-biostool", "program-from", "%s/BIOS.firmware" % self.firmPath]) == 0:
                secondary = True
            else:
                self.log.error("Unable to properly program secondary BIOS.")
        else:
            self.log.error("Unable to set secondary BIOS to active.")

        if primary and secondary:
            response.success = True
        elif primary:
            response.component = FW_BIOS
            response.success = False
            response.errorMessage = "Unable to properly program secondary BIOS."
        elif secondary:
            response.component = FW_BIOS
            response.success = False
            response.errorMessage = "Unable to properly program primary BIOS."
        else:
            response.component = FW_BIOS
            response.success = False
            response.errorMessage = "Unable to properly program BIOS."

        if reboot: self.reboot.put("REBOOT")

    ## Attempts to upgrade the I350 EEPROM using image included with QUAL
    #  @param   self
    #  @param   response    FirmwareUpdateResponse object
    #  @param   reboot      Reboot flag
    def updateI350EEPROM(self, response, reboot):
        response.success = True

        # TODO: Check that we are running on an MPS before calling tools that modify firmware
        if call(["eeupdate64e", "-nic=2", "-data", "%s/i350_mps.txt" % self.firmPath]) != 0:
            self.log.error("Unable to program I350 EEPROM.")
            response.component = FW_I350_EEPROM
            response.success = False
            response.errorMessage = "Unable to program I350 EEPROM."

        result = 0
        for nicidx in range(2, 6):
            result |= call(["bootutil64e", "-nic=%d" % nicidx, "-fe"])
        if result != 0:
            self.log.error("Unable to enable I350 flash.")
            response.component = FW_I350_EEPROM
            response.success = False
            response.errorMessage = "Unable to enable I350 flash."

        if reboot: self.reboot.put("REBOOT")

    ## Attempts to upgrade the I350 Flash using image included with QUAL
    #  @param   self
    #  @param   response    FirmwareUpdateResponse object
    #  @param   reboot      Reboot flag
    def updateI350Flash(self, response, reboot):
        response.success = True

        # TODO: Check that we are running on an MPS before calling tools that modify firmware
        if call(["i350-flashtool", "%s/i350_flash.bin" % self.firmPath]) != 0:
            self.log.error("Unable to program I350 flash.")
            response.component = FW_I350_FLASH
            response.success = False
            response.errorMessage = "Unable to program I350 flash."

        if reboot: self.reboot.put("REBOOT")

    ## Catches valid, unimplemented message command types.
    #  @param   self
    #  @param   response    FirmwareUpdateResponse object
    #  @param   reboot      Reboot flag
    def unimplemented(self, response, reboot):
        response.success = False
        response.errorMessage = "This message is not yet implemented."
        self.log.info("This message is not yet implemented.")

        if reboot: self.reboot.put("REBOOT")

    ## Waits for a reboot command, then attempts to reboot the system
    #  @param   self
    def rebooter(self):
        msg = self.reboot.get(block=True)

        sleep(.5)

        if msg == "REBOOT":
            call(["shutdown", "-r", "now"])

    ## Attempts to terminate module gracefully
    #  @param   self
    def terminate(self):
        self._running = False
        self.reboot.put("EXIT")
        self.stopThread()
