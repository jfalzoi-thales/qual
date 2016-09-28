import os
import socket
from ConfigParser import SafeConfigParser
from subprocess import call, check_call, check_output, CalledProcessError
from time import sleep
from paramiko import SSHClient, AutoAddPolicy, SSHException

from common.pb2.ErrorMessage_pb2 import ErrorMessage
from common.pb2.HDDS_API_pb2 import GetReq, GetResp, SetReq, SetResp
from qual.pb2.HDDS_pb2 import HostDomainDeviceServiceRequest, HostDomainDeviceServiceResponse
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.vtss.vtss import Vtss
from i350Inventory import I350Inventory
from semaInventory import SEMAInventory


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
        ## I350 inventory handler
        self.i350Inventory = I350Inventory(self.log)
        ## SEMA inventory handler
        self.semaInventory = SEMAInventory(self.log)
        ## BIOS tool command
        self.biosTool = "/thales/host/appliances/mps-biostool"

        #  Parse key names from Thales Host Domain Device Service configuration file
        thalesHDDSConfig = "/thales/host/config/HDDS.conv"
        configParser = SafeConfigParser()
        configParser.read(thalesHDDSConfig)
        ## List of valid HDDS keys
        self.inventoryKeys = []

        if configParser.sections() != []:
            for option in configParser.options("hdds_host_convertions"):
                if option.startswith("inventory"):
                    self.inventoryKeys.append(option)
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
            inventoryGetKeys = []
            ifeGetReq = None
            hddsGetReq = None

            for value in msg.body.values:
                if value.key.startswith("mac_address"):
                    if value.key.endswith("*"):
                        macGetKeys += self.macKeys
                    elif value.key in self.macKeys:
                        macGetKeys.append(value.key)
                    else:
                        self.log.warning("Attempted to get invalid mac address key: %s" % value.key)
                        self.addResp(response, value.key)
                elif value.key.startswith("inventory"):
                    if value.key.endswith("*"):
                        keyParts = value.key.split('.')

                        if len(keyParts) == 2:
                            inventoryGetKeys += self.inventoryKeys
                        elif len(keyParts) == 3:
                            for key in self.inventoryKeys:
                                if key.startswith("inventory.%s" % keyParts[1]):
                                    inventoryGetKeys.append(key)
                        else:
                            self.log.warning("Attempted to get invalid wildcard key: %s" % value.key)
                            self.addResp(response, value.key)
                    elif value.key in self.inventoryKeys or self.inventoryKeys == []:
                        inventoryGetKeys.append(value.key)
                    else:
                        self.log.warning("Attempted to get invalid inventory key: %s" % value.key)
                        self.addResp(response, value.key)
                elif value.key.startswith("ife"):
                    if ifeGetReq is None:
                        ifeGetReq = HostDomainDeviceServiceRequest()
                        ifeGetReq.requestType = HostDomainDeviceServiceRequest.GET

                    ifeValue = ifeGetReq.values.add()
                    ifeValue.key = value.key
                else:
                    if hddsGetReq is None: hddsGetReq = GetReq()
                    hddsGetReq.key.append(value.key)

            if macGetKeys:          self.macGet(response, macGetKeys)
            if inventoryGetKeys:    self.inventoryGet(response, inventoryGetKeys)
            if ifeGetReq:           self.ifeGet(response, ifeGetReq)
            if hddsGetReq:          self.hddsGet(response, hddsGetReq)
        elif msg.body.requestType == HostDomainDeviceServiceRequest.SET:
            macSetPairs = {}
            inventoryPairs = {}
            hddsSetReq = None

            for value in msg.body.values:
                if value.key.startswith("ife"):
                    self.log.warning("Attempted to set ife voltage or temperature.  Nothing to do.")
                    self.addResp(response, value.key, value.value)
                elif value.key.startswith("mac_address"):
                    if value.key in self.macKeys:
                        hex = value.value.replace(':','')

                        try:
                            if int(hex, 16) == 0: hex = ""
                        except ValueError: hex = ""

                        if len(hex) == 12:
                            macSetPairs[value.key] = value.value
                        else:
                            self.log.warning("Invalid MAC Address: %s" % value.value)
                            self.addResp(response, value.key, value.value)
                    else:
                        self.log.warning("Attempted to set invalid mac address key: %s" % value.key)
                        self.addResp(response, value.key, value.value)
                elif value.key.startswith("inventory"):
                    if value.key in self.inventoryKeys or self.inventoryKeys == []:
                        inventoryPairs[value.key] = value.value
                    else:
                        self.log.warning("Attempted to set invalid inventory key: %s" % value.key)
                        self.addResp(response, value.key, value.value)
                else:
                    if hddsSetReq is None: hddsSetReq = SetReq()
                    hddsValue = hddsSetReq.values.add()
                    hddsValue.key = value.key
                    hddsValue.value = value.value

            if macSetPairs:     self.macSet(response, macSetPairs)
            if inventoryPairs:  self.inventorySet(response, inventoryPairs)
            if hddsSetReq:      self.hddsSet(response, hddsSetReq)
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
    #  @param   ifeReq      A HostDomainDeviceServiceRequest object to be sent to the Guest VM QTA
    def ifeGet(self, response, ifeReq):
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

    ## Handles GET requests for HDDS
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     hddsReq   HostDomainDeviceServiceRequest object
    def hddsGet(self, response, hddsReq):
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

            self.addResp(response)

    ## Handles SET requests for MAC keys
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     macPairs  Dict containing pairs of keys and MAC address values to be set
    def macSet(self, response, macPairs):
        for key in macPairs:
            target = key.split('.')[-1]

            if target == "switch":
                self.vtssMacSet(response, key, macPairs[key])
            elif target == "processor":
                self.cpuMacSet(response, key, macPairs[key])
            elif target.startswith("i350_"):
                self.i350MacSet(response, key, macPairs[key])
            else:
                self.log.warning("Invalid or not yet supported key: %s" % key)
                self.addResp(response, key, macPairs[key])


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
        bank = "0"
        success = True

        try:
            getActive = check_output([self.biosTool, "get-active"])
            bank = getActive[0]
        except CalledProcessError:
            self.log.warning("Unable to get active BIOS bank.")

        try:
            if bank == "2":
                bank = "0"
                check_call([self.biosTool, "set-active", "0"])

            check_call([self.biosTool, "set-mac", mac])
            if check_output([self.biosTool, "get-mac"]).rstrip() != mac: success = False
            check_call([self.biosTool, "set-active", str(1 - int(bank))])
            check_call([self.biosTool, "set-mac", mac])
            if check_output([self.biosTool, "get-mac"]).rstrip() != mac: success = False

            # TODO: Confirm that get-mac reports mac addresses in the proper format
            self.addResp(response, key, mac, success)
        except CalledProcessError as err:
            self.log.warning("Unable to run %s" % err.cmd)
            self.addResp(response, key, mac)
        finally:
            call([self.biosTool, "set-active", bank])

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
            call(["eeupdate64e", "-nic=%d" % nicidx, "-a", macfile])

            if check_output(["eeupdate64e", "-nic=%d" % nicidx, "-mac_dump"]).splitlines()[-1] == i350mac:
                success = True

            if not success:
                self.log.error("Error programming %s", key)
            os.remove(macfile)

        self.addResp(response, key, mac, success)

    ## Handles SET requests for inventory items
    #  @param     self
    #  @param     response       HostDomainDeviceServiceResponse object
    #  @param     inventoryPairs Dict of inventory items
    def inventorySet(self, response, inventoryPairs):
        i350Pairs = {}
        semaPairs = {}

        # Validate keys/values and devide between carrier card (goes to I350)
        # and everything else (goes to SEMA flash)
        for key, value in inventoryPairs.items():
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
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     hddsReq   HostDomainDeviceServiceRequest object
    def hddsSet(self, response, hddsReq):
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
            elif response.name == "":
                self.log.warning("Set failed: No response from HDDS")
            else:
                self.log.warning("Unexpected response from HDDS: %s" % HDDSResp.name)

            self.addResp(response)
