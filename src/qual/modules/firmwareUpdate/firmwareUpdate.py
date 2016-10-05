import time
import os
import paramiko

from Queue import Queue
from subprocess import call

from common.pb2.GPIOManager_pb2 import RequestMessage, ResponseMessage
from qual.pb2.FirmwareUpdate_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
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
                          FW_SWITCH_FIRMWARE:       self.firmwareUpgrade,
                          FW_SWITCH_FIRMWARE_SWAP:  self.firmwareSwap,
                          FW_SWITCH_CONFIG:         self.configUpdate,
                          FW_SWITCH_CONFIG_SWAP:    self.configUpdateSwap}
        ## Location of firmware images
        self.firmPath = "/thales/qual/firmware"
        #  If not running on an MPS, point away from the directory containing MPS firmware
        if not (os.path.exists("/dev/mps/pci-audio") and os.path.exists("/dev/mps/pci-cpu-ethernet")):
            self.log.warning("Hardware does not appear to be an MPS; using test-firmware directory")
            self.firmPath = "/thales/qual/test-firmware"
        ## location of switch configuration
        self.configPath = "secondary-config"
        ## TFTP server for configurations
        self.tftpServer = "10.10.42.200"
        ## Switch IP
        self.switchAddress = '10.10.41.159'
        ## User name for switch
        self.switchUser = 'admin'
        ## Password for switch
        self.switchPassword = ''
        self.loadConfig(attributes=('switchAddress','switchUser','switchPassword', 'tftpServer'))
        ## Connection to GPIO manager
        self.gpioMgrClient = ThalesZMQClient("ipc:///tmp/gpio-mgr.sock", log=self.log, msgParts=1)
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
            return
        elif secondary:
            response.component = FW_BIOS
            response.success = False
            response.errorMessage = "Unable to properly program primary BIOS."
            return
        else:
            response.component = FW_BIOS
            response.success = False
            response.errorMessage = "Unable to properly program BIOS."
            return

        if reboot: self.reboot.put("REBOOT")

    ## Attempts to upgrade the I350 EEPROM using image included with QUAL
    #  @param   self
    #  @param   response    FirmwareUpdateResponse object
    #  @param   reboot      Reboot flag
    def updateI350EEPROM(self, response, reboot):
        response.success = True

        if call(["eeupdate64e", "-nic=2", "-data", "%s/I350_mps.txt" % self.firmPath]) != 0:
            self.log.error("Unable to program I350 EEPROM.")
            response.component = FW_I350_EEPROM
            response.success = False
            response.errorMessage = "Unable to program I350 EEPROM."
            return

        result = 0
        for nicidx in range(2, 6):
            result |= call(["bootutil64e", "-nic=%d" % nicidx, "-fe"])
        if result != 0:
            self.log.error("Unable to enable I350 flash.")
            response.component = FW_I350_EEPROM
            response.success = False
            response.errorMessage = "Unable to enable I350 flash."
            return

        if reboot: self.reboot.put("REBOOT")

    ## Attempts to upgrade the I350 Flash using image included with QUAL
    #  @param   self
    #  @param   response    FirmwareUpdateResponse object
    #  @param   reboot      Reboot flag
    def updateI350Flash(self, response, reboot):
        response.success = True

        if call(["i350-flashtool", "%s/1573_i350_flash.bin" % self.firmPath]) != 0:
            self.log.error("Unable to program I350 flash.")
            response.component = FW_I350_FLASH
            response.success = False
            response.errorMessage = "Unable to program I350 flash."
            return

        if reboot: self.reboot.put("REBOOT")

    ## Attempts to load the configuration update into the
    #  secondary config location
    #
    #  @param   self
    #  @param   response    FirmwareUpdateResponse object
    #  @param   reboot      Reboot flag
    def configUpdate(self, response, reboot):
        try:
            output = ''
            # Open the SSH connection
            switchClient = paramiko.SSHClient()
            switchClient.load_system_host_keys()
            switchClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            switchClient.connect(self.switchAddress, port=22,username=self.switchUser, password=self.switchPassword)
            # Execute the command
            # Need to open a channel; cause the switch doesn't support ssh command 'exec_command'
            channel = switchClient.invoke_shell()
            # Erase the secondary-config file just before transfer the updated
            channel.send("delete flash:secondary-config\n")
            while channel.recv_ready():
                output = channel.recv(1024)
            # Send the requested file to the switch
            channel.send("copy tftp://%s/%s flash:secondary-config\n" % (self.tftpServer, self.configPath))
            time.sleep(0.2)
            while channel.recv_ready():
                output = channel.recv(1024)
            # Check that the file was actually transferred
            while True:
                channel.send("dir\n")
                while channel.recv_ready():
                    output = channel.recv(1024)
                # if the file is being transferring, wait for it to finish
                if "operation is currently in progress" in output:
                    time.sleep(0.2)
                    continue
                if 'secondary-config' not in output:
                    # There was an error transferring the file
                    response.success = False
                    response.component = FW_SWITCH_CONFIG
                    response.errorMessage = "Error transfering file %s to secondary-file" % (self.configPath)
                    self.log.error("Error transfering file %s to secondary-file" % (self.configPath))
                    return
                break
            # Close the connection
            switchClient.close()
            # Fill the response
            response.success = True

            if reboot: self.reboot.put("REBOOT")

        except paramiko.ssh_exception.SSHException:
            response.success = False
            response.component = FW_SWITCH_CONFIG
            response.errorMessage = "Unable to establish the connection with %s" % (self.switchAddress)
            self.log.error("Unable to establish the connection with %s" % (self.switchAddress))
        except Exception as e:
            response.success = False
            response.component = FW_SWITCH_CONFIG
            response.errorMessage = "Unexpected error with connection. Error message: %s" % (e.message)
            self.log.error("Unexpected error with connection. Error message: %s" % (e.message))

    ## Attempts to swap the configuration update into the
    #  secondary config location
    #
    #  @param   self
    #  @param   response    FirmwareUpdateResponse object
    #  @param   reboot      Reboot flag
    def configUpdateSwap(self, response, reboot):
        try:
            output = ''
            # Open the SSH connection
            switchClient = paramiko.SSHClient()
            switchClient.load_system_host_keys()
            switchClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            switchClient.connect(self.switchAddress, port=22, username=self.switchUser, password=self.switchPassword)
            # Need to open a channel; cause the switch doesn't support ssh command 'exec_command'
            channel = switchClient.invoke_shell()

            while True:
                # Check that we have the secondary config file in the switch
                channel.send("dir\n")
                time.sleep(0.2)
                while channel.recv_ready():
                    output = channel.recv(1024)
                # This error may happen
                if "operation is currently in progress" in output:
                    time.sleep(0.2)
                    continue

                if "secondary-config" not in output:
                    response.success = False
                    response.component = FW_SWITCH_CONFIG_SWAP
                    response.errorMessage = "No Secondary file configuration present in the switch."
                    self.log.error("No Secondary file configuration present in the switch.")
                    return
                break

            ## Swap the configurations
            # 1-save the secondary config in an aux file
            channel.send("copy flash:secondary-config flash:aux-config\n")
            while channel.recv_ready():
                output = channel.recv(1024)
            # 2-copy the startup-config in the secondary-config
            channel.send("copy startup-config flash:secondary-config\n")
            while channel.recv_ready():
                output = channel.recv(1024)
            # 3-copy the saved secondary-config into the startup-config
            channel.send("copy flash:aux-config startup-config\n")
            while channel.recv_ready():
                output = channel.recv(1024)
            # 4-erase the auxiliar file
            time.sleep(0.2)
            channel.send("delete flash:aux-config\n")
            while channel.recv_ready():
                output = channel.recv(1024)

            # Close the connection
            switchClient.close()
            # Fill the response
            response.success = True

            if reboot: self.reboot.put("REBOOT")

        except paramiko.ssh_exception.SSHException as e:
            response.success = False
            response.component = FW_SWITCH_CONFIG_SWAP
            response.errorMessage = "Unable to establish the connection with %s" % (self.switchAddress)
            self.log.error("Unable to establish the connection with %s" % (self.switchAddress))
        except Exception as e:
            response.success = False
            response.component = FW_SWITCH_CONFIG_SWAP
            response.errorMessage = "Unexpected error with connection. Error message: %s" % (e.message)
            self.log.error("Unexpected error with connection. Error message: %s" % (e.message))

    ## Attempts to load a firmware image into
    #  the alternate location
    #
    #  @param   self
    #  @param   response    FirmwareUpdateResponse object
    #  @param   reboot      Reboot flag
    def firmwareUpgrade(self, response, reboot):
        try:
            output = ''
            # Open the SSH connection
            switchClient = paramiko.SSHClient()
            switchClient.load_system_host_keys()
            switchClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            switchClient.connect(self.switchAddress, port=22, username=self.switchUser, password=self.switchPassword)
            # Execute the command
            # Need to open a channel; cause the switch doesn't support ssh command 'exec_command'
            channel = switchClient.invoke_shell()

            # Copy the Firmware image into the switch
            channel.send("firmware upgrade tftp://%s/%s\n" % (self.tftpServer, "Thales-MPS.dat"))
            # Get the starting time of the upgrade operation
            startTime = time.time()
            # It should end in less than 8 minutes
            endTime = startTime + 480
            # Make some checks here
            while endTime > time.time():
                time.sleep(0.2)
                while channel.recv_ready():
                    output = channel.recv(1024)
                # if the tftp server is not active or wrong IP
                if "Invalid IP address" in output:
                    response.success = False
                    response.component = FW_SWITCH_FIRMWARE
                    response.errorMessage = "Switch unable to establish the connection with tftp server %s" % (self.tftpServer)
                    self.log.error("Switch unable to establish the connection with tftp server %s" % (self.tftpServer))
                    return
                # if Thales-MPS.dat was not present on the tftp server
                elif 'File not found' in output:
                    response.success = False
                    response.component = FW_SWITCH_FIRMWARE
                    response.errorMessage = "Switch unable to find \"Thales-MPS.dat\" image in tftp server %s" % (self.tftpServer)
                    self.log.error("Switch unable to find \"Thales-MPS.dat\" image in tftp server %s" % (self.tftpServer))
                    return
                # if Thales-MPS.dat was an invalid image
                elif 'Error: Invalid image' in output:
                    response.success = False
                    response.component = FW_SWITCH_FIRMWARE
                    response.errorMessage = "Invalid firmware image"
                    self.log.error("Invalid firmware image")
                    return
                else:
                    # Here we'll check if we are still connected to the switch,
                    # If not, it means that the switch accepted the file and it's upgrading
                    # otherwise, continue.......
                    transport = switchClient.get_transport()
                    if transport.is_active():
                        continue
                    else:
                        # Fill the response
                        response.success = True
                        # reboot if requested
                        if reboot: self.reboot.put("REBOOT")
                        return
            # If get here, it is because the switch was not able to upgrade
            response.success = False
            response.component = FW_SWITCH_FIRMWARE
            response.errorMessage = "FATAL! Firmware upgrade timeout."
            self.log.error("FATAL! Firmware upgrade timeout.")

        except paramiko.ssh_exception.SSHException:
            response.success = False
            response.component = FW_SWITCH_FIRMWARE
            response.errorMessage = "Unable to establish the connection with %s" % (self.switchAddress)
            self.log.error("Unable to establish the connection with %s" % (self.switchAddress))
        except Exception as e:
            response.success = False
            response.component = FW_SWITCH_FIRMWARE
            response.errorMessage = "Unexpected error with connection. Error message: %s" % (e.message)
            self.log.error("Unexpected error with connection. Error message: %s" % (e.message))

    ## Attempts to swap the firmware between the primary
    # location and the alternate location
    #
    #  @param   self
    #  @param   response    FirmwareUpdateResponse object
    #  @param   reboot      Reboot flag
    def firmwareSwap(self, response, reboot):
        try:
            output = ''
            # Open the SSH connection
            switchClient = paramiko.SSHClient()
            switchClient.load_system_host_keys()
            switchClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            switchClient.connect(self.switchAddress, port=22, username=self.switchUser, password=self.switchPassword)
            # Execute the command
            # Need to open a channel; cause the switch doesn't support ssh command 'exec_command'
            channel = switchClient.invoke_shell()

            # Copy the Firmware image into the switch
            channel.send("firmware swap\n")

            # TODO: Check operation result. Here we don't have a way to know if the switch swaped, I'm going to wait until we test it on the MPS to see what is the switch reponse in case of success or failure

            # Close the connection
            switchClient.close()
            # Fill the response
            response.success = True

            if reboot: self.reboot.put("REBOOT")

        except paramiko.ssh_exception.SSHException:
            response.success = False
            response.component = FW_SWITCH_FIRMWARE_SWAP
            response.errorMessage = "Unable to establish the connection with %s" % (self.switchAddress)
            self.log.error("Unable to establish the connection with %s" % (self.switchAddress))
        except Exception as e:
            response.success = False
            response.component = FW_SWITCH_CONFIG_SWAP
            response.errorMessage = "Unexpected error with connection. Error message: %s" % (e.message)
            self.log.error("Unexpected error with connection. Error message: %s" % (e.message))

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

        time.sleep(.5)

        if msg == "REBOOT":
            # Reboot the switch first by toggling its reset line low/high
            self.gpioSet("Reset_Vitesse7429", 0)
            time.sleep(.2)
            self.gpioSet("Reset_Vitesse7429", 1)
            # Now go ahead and reboot the CPU
            call(["shutdown", "-r", "now"])

    ## Call GPIO manager to set the state of a GPIO line
    #  @param   self
    #  @param   pin    Name of the GPIO pin to set
    #  @param   value  Value to which to set the pin (0 or 1)
    def gpioSet(self, pin, value):
        setReq = RequestMessage()
        setReq.pin_name = pin
        setReq.request_type = RequestMessage.SET
        setReq.value = value
        # We only use this for rebooting, so we won't bother looking at the response
        self.gpioMgrClient.sendRequest(ThalesZMQMessage(setReq))

    ## Attempts to terminate module gracefully
    #  @param   self
    def terminate(self):
        self._running = False
        self.reboot.put("EXIT")
        self.stopThread()
