import os
import socket
from ConfigParser import SafeConfigParser
from subprocess import call, check_output, CalledProcessError, Popen, PIPE
from time import sleep

from common.pb2.ErrorMessage_pb2 import ErrorMessage
from common.pb2.HDDS_API_pb2 import GetReq, GetResp, SetReq, SetResp
from i350Inventory import I350Inventory
from paramiko import SSHClient, AutoAddPolicy, SSHException
from qual.pb2.HDDS_pb2 import HostDomainDeviceServiceRequest, HostDomainDeviceServiceResponse
from semaInventory import SEMAInventory
from tklabs_utils.i350.eepromTools import EepromTools
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.vtss.vtss import Vtss


## HDDS Module
class HDDS(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config=None):
        #  Initialize parent class
        super(HDDS, self).__init__(config)
        ## Client connection to the Host Domain Device Service
        self.hddsClient = ThalesZMQClient("tcp://localhost:40001", log=self.log, timeout=2000)
        ## Name of CPU Ethernet device
        self.cpuEthernetDev = "enp0s31f6"
        ## Name of I350 Ethernet device
        self.i350EthernetDev = "ens1f"
        #  IP address of the switch
        self.switchAddress = "10.10.41.159"
        #  Username for switch communication
        self.switchUser = "admin"
        #  Password for switch communication
        self.switchPassword = ""
        ## Address for communicating with QTA running on the IFE VM
        self.ifeVmQtaAddr = "tcp://localhost:50003"
        self.loadConfig(attributes=('cpuEthernetDev', 'i350EthernetDev', 'switchAddress', 'switchUser', 'switchPassword', 'ifeVmQtaAddr'))
        ## Magic number for writing the CPU EEPROM
        self.cpuMagicNum = "0x15B78086"
        ## Connection to QTA running on the IFE VM
        self.ifeVmQtaClient = ThalesZMQClient(self.ifeVmQtaAddr, log=self.log, timeout=4000)
        ## SSH connection for programming switch MAC address
        self.sshClient = SSHClient()
        self.sshClient.set_missing_host_key_policy(AutoAddPolicy())
        ## Mac address types for handling wild cards
        self.macKeys = ["mac_address.switch",
                        "mac_address.processor",
                        "mac_address.i350_1",
                        "mac_address.i350_2",
                        "mac_address.i350_3",
                        "mac_address.i350_4"]
        ## Software part number types for handling wild cards
        self.swpnKeys = ["software_part.BIOS",
                         "software_part.i350_eeprom",
                         "software_part.i350_pxe",
                         "software_part.switch",
                         "software_part.ATP"]
        ## Software part number for ATP
        self.atpPartnum = "LV39-161008"
        ## I350 inventory handler
        self.i350Inventory = I350Inventory(self.log)
        ## SEMA inventory handler
        self.semaInventory = SEMAInventory(self.log)
        ## I350 EepromTools object lets us read I350 EEPROM
        self.i350eeprom = EepromTools(self.log)
        ## BIOS tool command
        self.biosTool = "/thales/host/appliances/mps-biostool"
        ## Flag to detect if running on MPSi
        self.ife = os.path.exists("/dev/mps/usb-mcp2221-ife")
        #  Parse key names from Thales Host Domain Device Service configuration file
        thalesHDDSConfig = "/thales/host/config/HDDS.conv"
        configParser = SafeConfigParser()
        configParser.read(thalesHDDSConfig)
        ## List of valid HDDS keys
        self.inventoryKeys = []

        if configParser.sections() != []:
            self.inventoryKeys = [option for option in configParser.options("hdds_host_convertions") if
                                  option.startswith("inventory")]
        else:
            self.log.warning("Missing or Empty Configuration File: %s" % thalesHDDSConfig)

        #  Add handler to available message handlers
        self.addMsgHandler(HostDomainDeviceServiceRequest, self.handler)

    ## Handles incoming messages
    #  Receives tzmq request and runs requested process
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  ThalesZMQMessage object
    def handler(self, msg):
        response = HostDomainDeviceServiceResponse()

        #  Split up the requests by key type and handle them
        if msg.body.requestType == HostDomainDeviceServiceRequest.GET:
            macGetKeys = []
            swpnGetKeys = []
            inventoryGetKeys = []
            ifeGetKeys = []
            hddsGetKeys = []

            for value in msg.body.values:
                if value.key.startswith("mac_address."):
                    if value.key[-1] == "*":
                        macGetKeys.extend(self.macKeys)
                    elif value.key in self.macKeys:
                        macGetKeys.append(value.key)
                    else:
                        self.log.warning("Attempted to get invalid mac address key: %s" % value.key)
                        self.addResp(response, value.key)
                elif value.key.startswith("software_part."):
                    if value.key[-1] == "*":
                        swpnGetKeys.extend(self.swpnKeys)
                    elif value.key in self.swpnKeys:
                        swpnGetKeys.append(value.key)
                    else:
                        self.log.warning("Attempted to get invalid software key: %s" % value.key)
                        self.addResp(response, value.key)
                elif value.key.startswith("inventory."):
                    if value.key[-1] == "*":
                        keyParts = value.key.split('.')

                        if len(keyParts) == 2:
                            for key in self.inventoryKeys:
                                if self.ife and key.startswith("inventory.ife."):
                                    ifeGetKeys.append(key)
                                else:
                                    inventoryGetKeys.append(key)
                        elif len(keyParts) == 3:
                            for key in self.inventoryKeys:
                                if key.startswith("inventory.%s" % keyParts[1]):
                                    if self.ife and keyParts[1] == "ife":
                                        ifeGetKeys.append(key)
                                    else:
                                        inventoryGetKeys.append(key)
                        else:
                            self.log.warning("Attempted to get invalid wildcard key: %s" % value.key)
                            self.addResp(response, value.key)
                    elif value.key in self.inventoryKeys or self.inventoryKeys == []:
                        if self.ife and value.key.startswith("inventory.ife."):
                            ifeGetKeys.append(value.key)
                        else:
                            inventoryGetKeys.append(value.key)
                    else:
                        self.log.warning("Attempted to get invalid inventory key: %s" % value.key)
                        self.addResp(response, value.key)
                elif value.key.startswith("ife"):
                    ifeGetKeys.append(value.key)
                else:
                    hddsGetKeys.append(value.key)

            if macGetKeys:          self.macGet(response, macGetKeys)
            if swpnGetKeys:         self.swpnGet(response, swpnGetKeys)
            if inventoryGetKeys:    self.inventoryGet(response, inventoryGetKeys)
            if ifeGetKeys:          self.ifeGet(response, ifeGetKeys)
            if hddsGetKeys:         self.hddsGet(response, hddsGetKeys)
        elif msg.body.requestType == HostDomainDeviceServiceRequest.SET:
            macSetPairs = {}
            inventorySetPairs = {}
            ifeSetPairs = {}
            hddsSetPairs = {}

            for value in msg.body.values:
                if value.key.startswith("mac_address."):
                    if value.key in self.macKeys:
                        hexchars = value.value.replace(':','')

                        try:
                            if int(hexchars, 16) == 0: hexchars = ""
                        except ValueError: hexchars = ""

                        if len(hexchars) == 12:
                            macSetPairs[value.key] = value.value
                        else:
                            self.log.warning("Invalid MAC Address: %s" % value.value)
                            self.addResp(response, value.key, value.value)
                    else:
                        self.log.warning("Attempted to set invalid mac address key: %s" % value.key)
                        self.addResp(response, value.key, value.value)
                elif value.key.startswith("inventory."):
                    if value.key in self.inventoryKeys or self.inventoryKeys == []:
                        if self.ife and value.key.startswith("inventory.ife."):
                            ifeSetPairs[value.key] = value.value
                        else:
                            inventorySetPairs[value.key] = value.value
                    else:
                        self.log.warning("Attempted to set invalid inventory key: %s" % value.key)
                        self.addResp(response, value.key, value.value)
                elif value.key.startswith("ife.") or value.key.startswith("software_part."):
                    self.log.warning("Attempted to set read-only key %s", value.key)
                    self.addResp(response, value.key, value.value)
                else:
                    hddsSetPairs[value.key] = value.value

            if macSetPairs:         self.macSet(response, macSetPairs)
            if inventorySetPairs:   self.inventorySet(response, inventorySetPairs)
            if ifeSetPairs:         self.ifeSet(response, ifeSetPairs)
            if hddsSetPairs:        self.hddsSet(response, hddsSetPairs)
        else:
            self.log.error("Unexpected Request Type %d" % msg.body.requestType)

        return ThalesZMQMessage(response)

    ## Adds another set of values to the repeated property response field
    #  @param   self
    #  @param   response    A HostDomainDeviceServiceResponse object
    #  @param   key         Key to be added to response, default empty
    #  @param   value       Value of key to be added to response, default empty
    #  @param   success     Success flag to be added to response, default False
    def addResp(self, response, key="", value="", success=False):
        respVal = response.values.add()
        respVal.key = key
        respVal.value = value
        respVal.success = success

    ## Sends SSH command and returns output
    #  @param   self
    #  @param   shell   Shell to send commands to via SSH
    #  @param   cmd     Command to be sent via SSH
    #  @return  out     Output received from shell
    def sendShell(self, shell, cmd):
        out = ""
        shell.send("%s\n" % cmd)

        while True:
            sleep(.1)

            if shell.recv_ready():
                while shell.recv_ready():
                    sleep(.1)
                    out += shell.recv(1024)

                break

        return out

    ## Handles GET requests for IFE keys
    #  @param   self
    #  @param   response    A HostDomainDeviceServiceResponse object
    #  @param   ifeKeys     A list of keys to be sent to the Guest VM QTA
    def ifeGet(self, response, ifeKeys):
        ifeReq = HostDomainDeviceServiceRequest()
        ifeReq.requestType = HostDomainDeviceServiceRequest.GET

        for key in ifeKeys:
            value = ifeReq.values.add()
            value.key = key

        # IFE get messages are handled by the QTA running on the IFE VM
        ifeVmQtaResponse = self.ifeVmQtaClient.sendRequest(ThalesZMQMessage(ifeReq))

        if ifeVmQtaResponse.name == "HostDomainDeviceServiceResponse":
            deserializedResponse = HostDomainDeviceServiceResponse()
            deserializedResponse.ParseFromString(ifeVmQtaResponse.serializedBody)

            for value in deserializedResponse.values:
                self.addResp(response, value.key, value.value, value.success)
        else:
            self.log.error("Unexpected response from IFE VM HDDS: %s" % ifeVmQtaResponse.name)
            self.addResp(response)

    ## Handles GET requests for MAC keys
    #  @param   self
    #  @param   response    A HostDomainDeviceServiceResponse object
    #  @param   macKeys     A list of keys used for requesting MAC addresses
    def macGet(self, response, macKeys):
        for key in macKeys:
            target = key.split('.')[-1]

            if target == "switch":
                self.vtssMacGet(response, key)
            elif target == "processor":
                self.nicMacGet(response, key, self.cpuEthernetDev)
            elif target.startswith("i350"):
                self.nicMacGet(response, key, self.i350EthernetDev + str(int(target[-1]) - 1))
            else:
                self.log.warning("Invalid or not yet supported mac address key: %s" % key)
                self.addResp(response, key)

    ## Handles GET requests for switch MAC key
    #  @param   self
    #  @param   response    A HostDomainDeviceServiceResponse object
    #  @param   key         Key of MAC address to be obtained
    def vtssMacGet(self, response, key):
        try:
            vtss = Vtss(self.switchAddress)
            json = vtss.callMethod(["ip.status.interface.link.get"])
            mac = json["result"][0]["val"]["macAddress"]
        except (socket.error, KeyError, IndexError):
            mac = ""

        if mac:
            self.addResp(response, key, mac, True)
        else:
            self.log.warning("Unable to retrieve switch MAC address.")
            self.addResp(response, key)

    ## Handles GET requests for CPU and I350 card MAC keys
    #  @param   self
    #  @param   response    A HostDomainDeviceServiceResponse object
    #  @param   key         Key of MAC address to be obtained
    #  @param   device      Device who's MAC address is being obtained
    def nicMacGet(self, response, key, device):
        try:
            mac = check_output(["cat", "/sys/class/net/%s/address" % device])
            self.addResp(response, key, mac.rstrip('\n'), True)
        except CalledProcessError as err:
            self.log.warning("Unable to run %s" % err.cmd)
            self.addResp(response, key)

    ## Handles GET requests for I350 inventory keys
    #  @param     self
    #  @param     response      HostDomainDeviceServiceResponse object
    #  @param     inventoryKeys List of keys to get
    def inventoryGet(self, response, inventoryKeys):
        inventoryValues = {}
        self.i350Inventory.read(inventoryValues)
        self.semaInventory.read(inventoryValues)

        for key in inventoryKeys:
            if key in inventoryValues:
                self.addResp(response, key, inventoryValues[key], True)
            elif key in self.inventoryKeys:
                self.addResp(response, key, "", True)
            else:
                self.log.warning("Attempted to get unrecognized inventory key: %s" % key)
                self.addResp(response, key)

    ## Handles GET requests for software_part keys
    #  @param   self
    #  @param   response    A HostDomainDeviceServiceResponse object
    #  @param   macKeys     A list of keys used for requesting MAC addresses
    def swpnGet(self, response, macKeys):
        for key in macKeys:
            target = key.split('.')[-1]

            if target == "BIOS":
                self.biosSwpnGet(response, key)
            elif target == "i350_eeprom":
                self.i350eepromSwpnGet(response, key)
            elif target == "i350_pxe":
                self.i350pxeSwpnGet(response, key)
            elif target == "switch":
                self.vtssSwpnGet(response, key)
            elif target == "ATP":
                self.atpSwpnGet(response, key)


    ## Handles GET requests for BIOS software part number
    #  @param     self
    #  @param     response      HostDomainDeviceServiceResponse object
    #  @param     inventoryKeys List of keys to get
    def biosSwpnGet(self, response, key):
        try:
            lines = check_output(['amidewrap' ,'/SS', '/SV']).splitlines()
        except (CalledProcessError, OSError):
            self.log.error('Unable to retrieve BIOS information.')
            self.addResp(response, key)
        else:
            partnum = None
            version = None
            for line in lines:
                if 'System Serial number' in line:
                    line = line.split(" ")
                    partnum = line[-1].strip('"')
                elif 'System version' in line:
                    line = line.split(" ")
                    version = line[-1].strip('"')

            if partnum and version:
                self.addResp(response, key, partnum + '_' + version, True)
            else:
                self.log.error('Unable to parse BIOS information.')
                self.addResp(response, key)

    ## Handles GET requests for I350 EEPROM software part number
    #  @param     self
    #  @param     response      HostDomainDeviceServiceResponse object
    #  @param     inventoryKeys List of keys to get
    def i350eepromSwpnGet(self, response, key):
        # Read version word from EEPROM
        eePromValue = self.i350eeprom.readWord(0x0a)
        if eePromValue is not None:
            majorVersion = (eePromValue & 0xf000) >> 12
            minorVersion = eePromValue & 0xff

            # OEM version number is in a different EEPROM word
            eePromValue = self.i350eeprom.readWord(0x0c)
            if eePromValue is not None:
                oem = eePromValue
                # If we reach this point, we have the major and the minor version, and the OEM
                # We can construct the complete version number
                # I350 doesn't have its own part number, we use the ATP part number
                self.addResp(response, key, "%s_%d.%d.%d" % (self.atpPartnum, majorVersion, minorVersion, oem), True)
            else:
                self.log.error('Unable to get I350 EEPROM OEM version.')
                self.addResp(response, key)
        else:
            self.log.error('Unable to get I350 EEPROM version.')
            self.addResp(response, key)

    ## Handles GET requests for I350 PXE Firmware software part number
    #  @param     self
    #  @param     response      HostDomainDeviceServiceResponse object
    #  @param     inventoryKeys List of keys to get
    def i350pxeSwpnGet(self, response, key):
        # Read PXE Firmware version word from EEPROM
        eePromValue = self.i350eeprom.readWord(0x64)
        if eePromValue is not None:
            majorVersion = (eePromValue & 0xf000) >> 12
            minorVersion = (eePromValue & 0xf00) >> 8
            buildNumber  = eePromValue & 0xff
            # If we reach this point, we have the major and the minor version, and the OEM
            # We can construct the complete version number
            # I350 doesn't have its own part number, we use the ATP part number
            self.addResp(response, key, "%s_%d.%d.%d" % (self.atpPartnum, majorVersion, minorVersion, buildNumber), True)
        else:
            self.log.error('Unable to get I350 PXE version.')
            self.addResp(response, key)

    ## Handles GET requests for switch software part number
    #  @param     self
    #  @param     response      HostDomainDeviceServiceResponse object
    #  @param     inventoryKeys List of keys to get
    def vtssSwpnGet(self, response, key):
        try:
            # Open connection with the switch
            vtss = Vtss(switchIP=self.switchAddress)
            # Get the firmware version
            jsonResp = vtss.callMethod(['firmware.status.switch.get'])
            # If no error, look for something in the string that looks like a version number
            if jsonResp['error'] is None:
                partnum = None
                version = None
                for item in jsonResp['result'][0]['val']['Version'].split():
                    if item[0].isdigit():
                        version = item
                        break
                    else:
                        partnum = item
                if partnum and version:
                    self.addResp(response, key, "%s_%s" % (partnum, version), True)
                else:
                    self.log.error('Unable to parse switch version information.')
                    self.addResp(response, key)
                return
            else:
                self.log.error('Error retrieving the information from the switch.')
                self.addResp(response, key)
        except Exception:
            self.log.error('Unable to retrieve the information from the switch.')
            self.addResp(response, key)

    ## Handles GET requests for ATP software part number
    #  @param     self
    #  @param     response      HostDomainDeviceServiceResponse object
    #  @param     inventoryKeys List of keys to get
    def atpSwpnGet(self, response, key):
        try:
            version = check_output(["rpm", "-q", "--queryformat=%{VERSION}", "qual"])
        except CalledProcessError:
            self.log.warning("Unable to get ATP version number.")
            self.addResp(response, key)
        else:
            self.addResp(response, key, "%s_%s" % (self.atpPartnum, version), True)

    ## Handles GET requests for HDDS
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     hddsKeys  List of keys to be sent to the HDDS
    def hddsGet(self, response, hddsKeys):
        hddsReq = GetReq()
        hddsReq.key.extend(hddsKeys)
        #  Just pass through to the actual HDDS service
        HDDSResp = self.hddsClient.sendRequest(ThalesZMQMessage(hddsReq))

        #  Check that we got back the expected response
        if HDDSResp.name == "GetResp":
            getResp = GetResp()
            getResp.ParseFromString(HDDSResp.serializedBody)

            for value in getResp.values:
                self.addResp(response, value.keyValue.key, value.keyValue.value, value.success)
                if not value.success:
                    self.log.warning("HDDS error for get %s: %s" % (value.keyValue.key, value.error.error_description))
        else:
            if HDDSResp.name == "ErrorMessage":
                err = ErrorMessage()
                err.ParseFromString(HDDSResp.serializedBody)
                self.log.warning("Got error message from HDDS: %s" % err.error_description)
            elif HDDSResp.name == "":
                self.log.warning("Get failed: No response from HDDS")
            else:
                self.log.warning("Unexpected response from HDDS: %s" % HDDSResp.name)

            for key in hddsKeys:
                self.addResp(response, key)


    ## Handles SET requests for MAC keys
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     macPairs  Dict containing pairs of keys and MAC address values to be set
    def macSet(self, response, macPairs):
        for key, value in macPairs.items():
            target = key.split('.')[-1]

            if target == "switch":
                self.vtssMacSet(response, key, value)
            elif target == "processor":
                self.cpuMacSet(response, key, value)
            elif target.startswith("i350_"):
                self.i350MacSet(response, key, value)
            else:
                self.log.warning("Invalid or not yet supported key: %s" % key)
                self.addResp(response, key, value)


    ## Handles SET requests for vtss MAC key
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     key       Key of MAC address to be set
    #  @param     mac       MAC address to be set
    def vtssMacSet(self, response, key, mac):
        switchMac = mac.replace(':', '-')

        try:
            self.sshClient.connect(self.switchAddress, 22, self.switchUser, self.switchPassword)
            shell = self.sshClient.invoke_shell()
            self.sendShell(shell, "platform debug allow")
            self.sendShell(shell, "debug board mac %s" % switchMac)
            out = self.sendShell(shell, "debug board")
            self.sshClient.close()
        except SSHException:
            self.log.error("Problem communicating with switch via SSH.")
            self.addResp(response, key, mac)
        else:
            if out and out.split()[6] == switchMac.lower():
                self.addResp(response, key, mac, True)
            else:
                self.log.warning("Unable to set switch MAC address.")
                self.addResp(response, key, mac)

    ## Handles SET requests for CPU MAC key
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     key       Key of MAC address to be set
    #  @param     mac       MAC address to be set
    def cpuMacSet(self, response, key, mac):
        byteMac = bytearray.fromhex(mac.replace(':', ''))

        self.log.info("Writing CPU MAC Address to EEPROM")
        cmd = ['ethtool', '-E', self.cpuEthernetDev, 'magic', self.cpuMagicNum, 'offset', '0x00']
        self.log.debug("Writing %d bytes to command: %s" % (len(byteMac), " ".join(cmd)))
        ethtool = Popen(cmd, stdin=PIPE)
        ethtool.stdin.write(byteMac)
        ethtool.stdin.close()
        rc = ethtool.wait()
        self.log.debug("ethtool command returned: %d" % rc)

        self.addResp(response, key, mac, True) if rc == 0 else self.addResp(response, key, mac)

    ## Handles SET requests for I350 MAC key
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     key       Key of MAC address to be set
    #  @param     mac       MAC address to be set
    def i350MacSet(self, response, key, mac):
        success = False
        # Key is 1,2,3,4 but NIC index for eeupdate tool is 2,3,4,5
        nicidx = int(key[-1]) + 1
        # Write the MAC address to a file
        macfile = "/tmp/i350_mac.txt"
        i350mac = mac.replace(':', '')
        if os.path.exists(macfile):
            os.remove(macfile)
        try:
            with open(macfile, 'w') as macfileObj:
                macfileObj.write(i350mac + '\n')
        except IOError:
            self.log.error("Unable to write file for %s", key)
        else:
            # Actually program the MAC address
            if call(["eeupdate64e", "-nic=%d" % nicidx, "-a", macfile]) == 0:
                success = True
            if not success:
                self.log.error("Error programming %s", key)
            os.remove(macfile)

        self.addResp(response, key, mac, success)

    ## Handles SET requests for IFE keys
    #  @param   self
    #  @param   response    A HostDomainDeviceServiceResponse object
    #  @param   ifePairs    Dict of key value pairs to be sent to the Guest VM QTA
    def ifeSet(self, response, ifePairs):
        ifeReq = HostDomainDeviceServiceRequest()
        ifeReq.requestType = HostDomainDeviceServiceRequest.SET

        for key, value in ifePairs.items():
            ifeValue = ifeReq.values.add()
            ifeValue.key = key
            ifeValue.value = value

        # IFE set messages are handled by the QTA running on the IFE VM
        ifeVmQtaResponse = self.ifeVmQtaClient.sendRequest(ThalesZMQMessage(ifeReq))

        if ifeVmQtaResponse.name == "HostDomainDeviceServiceResponse":
            deserializedResponse = HostDomainDeviceServiceResponse()
            deserializedResponse.ParseFromString(ifeVmQtaResponse.serializedBody)

            for value in deserializedResponse.values:
                self.addResp(response, value.key, value.value, value.success)
        else:
            self.log.error("Unexpected response from IFE VM HDDS: %s" % ifeVmQtaResponse.name)
            self.addResp(response)

    ## Handles SET requests for inventory items
    #  @param     self
    #  @param     response          HostDomainDeviceServiceResponse object
    #  @param     inventorySetPairs Dict of inventory items
    def inventorySet(self, response, inventorySetPairs):
        i350Pairs = {}
        semaPairs = {}

        # Validate keys/values and devide between carrier card (goes to I350)
        # and everything else (goes to SEMA flash)
        for key, value in inventorySetPairs.items():
            # Key has form inventory.<section>.<item>
            if key.split('.')[1] == "carrier_card":
                i350Pairs[key] = value
            else:
                semaPairs[key] = value

        # Update the SEMA inventory area
        if len(semaPairs) > 0:
            success = self.semaInventory.update(semaPairs)
            for key, value in semaPairs.items():
                self.addResp(response, key, value, success)

        # Update the I350 inventory area
        if len(i350Pairs) > 0:
            success = self.i350Inventory.update(i350Pairs)
            for key, value in i350Pairs.items():
                self.addResp(response, key, value, success)

    ## Handles SET requests for HDDS
    #  @param     self
    #  @param     response      HostDomainDeviceServiceResponse object
    #  @param     hddsPairs     A Dict of key value pairs to be set by the HDDS
    def hddsSet(self, response, hddsPairs):
        hddsReq = SetReq()

        for key, value in hddsPairs.items():
            hddsValue = hddsReq.values.add()
            hddsValue.key = key
            hddsValue.value = value

        #  Just pass through to the actual HDDS service
        HDDSResp = self.hddsClient.sendRequest(ThalesZMQMessage(hddsReq))

        #  Check that we got back the expected response
        if HDDSResp.name == "SetResp":
            setResp = SetResp()
            setResp.ParseFromString(HDDSResp.serializedBody)

            for value in setResp.values:
                self.addResp(response, value.keyValue.key, value.keyValue.value, value.success)
                if not value.success:
                    self.log.warning("HDDS error for set %s: %s" % (value.keyValue.key, value.error.error_description))
        else:
            if HDDSResp.name == "ErrorMessage":
                err = ErrorMessage()
                err.ParseFromString(HDDSResp.serializedBody)
                self.log.warning("Got error message from HDDS: %s" % err.error_description)
            elif HDDSResp.name == "":
                self.log.warning("Set failed: No response from HDDS")
            else:
                self.log.warning("Unexpected response from HDDS: %s" % HDDSResp.name)

            for key, value in hddsPairs.items():
                self.addResp(response, key, value)
