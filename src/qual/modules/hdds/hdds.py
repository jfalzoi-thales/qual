from subprocess import call, check_call, check_output, CalledProcessError
import os

from common.pb2.ErrorMessage_pb2 import ErrorMessage
from common.pb2.HDDS_API_pb2 import GetReq, GetResp, SetReq, SetResp
from qual.pb2.HDDS_pb2 import HostDomainDeviceServiceRequest, HostDomainDeviceServiceResponse
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
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
        ## Address for communicating with QTA running on the IFE VM
        self.ifeVmQtaAddr = "tcp://localhost:50003"
        self.loadConfig(attributes=('ifeVmQtaAddr', 'cpuEthernetDev', 'i350EthernetDev'))
        ## Connection to QTA running on the IFE VM
        self.ifeVmQtaClient = ThalesZMQClient(self.ifeVmQtaAddr, log=self.log, timeout=3000)
        ## Mac address types for handling wild cards
        self.macTypes = ["mac_address.processor",
                         "mac_address.i350_1",
                         "mac_address.i350_2",
                         "mac_address.i350_3",
                         "mac_address.i350_4"]
        ## Inventory item length limits
        self.lengthLimits = {"part_number":        24,
                             "serial_number":      24,
                             "revision":           8,
                             "manufacturer_pn":    24,
                             "manufacturing_date": 8,
                             "manufacturer_name":  24,
                             "manufacturer_cage":  8}
        ## I350 inventory handler
        self.i350Inventory = I350Inventory(self.log)
        ## SEMA inventory handler
        self.semaInventory = SEMAInventory(self.log)
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
            ifeGetReq = None
            macGetKeys = None
            inventoryGetKeys = None
            hddsGetReq = None

            for value in msg.body.values:
                if value.key.startswith("ife"):
                    if ifeGetReq is None:
                        ifeGetReq = HostDomainDeviceServiceRequest()
                        ifeGetReq.requestType = HostDomainDeviceServiceRequest.GET

                    ifeValue = ifeGetReq.values.add()
                    ifeValue.key = value.key
                elif value.key.startswith("mac_address"):
                    if macGetKeys is None: macGetKeys = []

                    if value.key.endswith("*"):
                        macGetKeys += self.macTypes
                    else:
                        macGetKeys.append(value.key)
                elif value.key == "inventory.*":
                    # Get carrier_card inventory using local function, get everything else from HDDS
                    if inventoryGetKeys is None: inventoryGetKeys = []
                    inventoryGetKeys.append("inventory.carrier_card.*")
                    if hddsGetReq is None: hddsGetReq = GetReq()
                    hddsGetReq.key.append(value.key)
                elif value.key.startswith("inventory.carrier_card"):
                    if inventoryGetKeys is None: inventoryGetKeys = []
                    inventoryGetKeys.append(value.key)
                else:
                    if hddsGetReq is None: hddsGetReq = GetReq()
                    hddsGetReq.key.append(value.key)

            if ifeGetReq is not None: self.ifeGet(response, ifeGetReq)
            if macGetKeys is not None: self.macGet(response, macGetKeys)
            if inventoryGetKeys is not None: self.inventoryGet(response, inventoryGetKeys)
            if hddsGetReq is not None: self.hddsGet(response, hddsGetReq)
        elif msg.body.requestType == HostDomainDeviceServiceRequest.SET:
            macSetPairs = None
            inventoryPairs = None
            hddsSetReq = None

            for value in msg.body.values:
                if value.key.startswith("ife"):
                    self.log.warning("Attempted to set ife voltage or temperature.  Nothing to do.")
                    self.addResp(response, value.key)
                elif value.key.startswith("mac_address"):
                    if macSetPairs is None: macSetPairs = {}
                    macSetPairs[value.key] = value.value
                elif value.key.startswith("inventory"):
                    if inventoryPairs is None: inventoryPairs = {}
                    inventoryPairs[value.key] = value.value
                else:
                    if hddsSetReq is None: hddsSetReq = SetReq()
                    hddsValue = hddsSetReq.values.add()
                    hddsValue.key = value.key
                    hddsValue.value = value.value

            if macSetPairs is not None: self.macSet(response, macSetPairs)
            if inventoryPairs is not None: self.inventorySet(response, inventoryPairs)
            if hddsSetReq is not None: self.hddsSet(response, hddsSetReq)
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
            target = key.split('.')[1]

            if target.startswith("processor"):
                self.nicMacGet(response, key, self.cpuEthernetDev)
            elif target.startswith("i350"):
                self.nicMacGet(response, key, self.i350EthernetDev + str(int(target[-1]) - 1))
            else:
                self.log.warning("Invalid or not yet supported key: %s" % key)
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
        i350Values = self.i350Inventory.read()

        for key in inventoryKeys:
            item = key.split('.')[2]
            if item == '*':
                for ikey, ivalue in i350Values.items():
                    self.addResp(response, ikey, ivalue, True)
            elif item in i350Values:
                self.addResp(response, key, i350Values[key], True)
            elif item in self.lengthLimits:
                self.addResp(response, key, "", True)
            else:
                self.log.warning("Attempt to get invalid key: %s" % key)
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
                # Blacklist inventory.carrier_card values from HDDS, we don't trust them
                if not value.keyValue.key.startswith("inventory.carrier_card"):
                    self.addResp(response, value.keyValue.key, value.keyValue.value, value.success)
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
            # TODO: Validate that value looks like a MAC address
            target = key.split('.')[1]

            if target.startswith("processor"):
                self.cpuMacSet(response, key, macPairs[key])
            if target.startswith("i350_"):
                self.i350MacSet(response, key, macPairs[key])
            else:
                self.log.warning("Invalid or not yet supported key: %s" % key)
                self.addResp(response, key, macPairs[key])

    ## Handles SET requests for CPU MAC key
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     key       Key of MAC address to be set
    #  @param     mac       MAC address to be set
    def cpuMacSet(self, response, key, mac):
        bank = "0"

        try:
            getActive = check_output(["mps-biostool", "get-active"])
            bank = getActive[0]
        except CalledProcessError:
            self.log.warning("Unable to get active BIOS bank.")

        try:
            if bank == "2":
                bank = "0"
                check_call(["mps-biostool", "set-active", "0"])

            check_call(["mps-biostool", "set-mac", mac])
            check_call(["mps-biostool", "set-active", str(1 - int(bank))])
            check_call(["mps-biostool", "set-mac", mac])
            self.addResp(response, key, mac, True)
        except CalledProcessError as err:
            self.log.warning("Unable to run %s" % err.cmd)
            self.addResp(response, key, mac)
        finally:
            call(["mps-biostool", "set-active", bank])

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
        if os.path.exists(macfile):
            os.remove(macfile)
        try:
            with open(macfile, 'w') as macfileObj:
                macfileObj.write(mac.replace(':', '') + '\n')
        except IOError:
            self.log.error("Unable to write file for %s", key)
        else:
            # Actually program the MAC address
            success = (call(["eeupdate64e", "-nic=%d" % nicidx, "-a", macfile]) == 0)
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
            splitKey = key.split('.')
            section = splitKey[1]
            item = splitKey[2]
            if item not in self.lengthLimits and key not in ("inventory.lru.name", "inventory.lru.weight", "inventory.lru.mod_dot_level"):
                self.log.warning("Attempt to set invalid key %s" % key)
                self.addResp(response, key, value)
            elif section == "carrier_card":
                i350Pairs[key] = value
            else:
                semaPairs[key] = value

        # Update the I350 inventory area
        if len(i350Pairs) > 0:
            success = self.i350Inventory.update(i350Pairs)
            for key, value in i350Pairs.items():
                self.addResp(response, key, value, success)

        # Update the SEMA inventory area
        if len(semaPairs) > 0:
            success = self.semaInventory.update(semaPairs)
            for key, value in semaPairs.items():
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
