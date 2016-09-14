from subprocess import call, check_output

from common.pb2.ErrorMessage_pb2 import ErrorMessage
from common.pb2.HDDS_API_pb2 import GetReq, GetResp, SetReq, SetResp
from qual.pb2.HDDS_pb2 import HostDomainDeviceServiceRequest, HostDomainDeviceServiceResponse
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


## HDDS Module
class HDDS(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    #  @param   deserialize     Flag to deserialize the responses when running unit test
    def __init__(self, config=None, deserialize=False):
        #  Initialize parent class
        super(HDDS, self).__init__(config)
        ## Client connection to the Host Domain Device Service
        self.hddsClient = ThalesZMQClient("tcp://localhost:40001", log=self.log, timeout=2000)
        ## Name of CPU Ethernet device
        self.cpuEthernetDev = "eno1"
        ## Name of I350 Ethernet device
        self.i350EthernetDev = "ens1f"
        ## Address for communicating with QTA running on the IFE VM
        self.ifeVmQtaAddr = "tcp://localhost:50003"
        self.loadConfig(attributes=('ifeVmQtaAddr', 'cpuEthernetDev', 'i350EthernetDev'))
        ## Connection to QTA running on the IFE VM
        self.ifeVmQtaClient = ThalesZMQClient(self.ifeVmQtaAddr, log=self.log)
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
            hddsGetReq = None

            for value in msg.body.values:
                if value.key.startswith(("ife.voltage", "ife.temperature")):
                    if ifeGetReq is None: ifeGetReq = HostDomainDeviceServiceRequest()
                    ifeGetReq.requestType = HostDomainDeviceServiceRequest.GET
                    ifeValue = ifeGetReq.values.add()
                    ifeValue.key = value.key
                elif value.key.startswith("mac_address"):
                    if macGetKeys is None: macGetKeys = []
                    macGetKeys.append(value.key)
                else:
                    if hddsGetReq is None: hddsGetReq = GetReq()
                    hddsGetReq.key.append(value.key)

            if ifeGetReq is not None: self.ifeGet(response, ifeGetReq)
            if macGetKeys is not None: self.macGet(response, macGetKeys)
            if hddsGetReq is not None: self.hddsGet(response, hddsGetReq)
        elif msg.body.requestType == HostDomainDeviceServiceRequest.SET:
            macSetPairs = None
            hddsSetReq = None

            for value in msg.body.values:
                if value.key.startswith(("ife.voltage", "ife.temperature")):
                    self.log.warning("Attempted to set ife voltage or temperature.  Nothing to do.")
                    self.addResp(response, value.key)
                elif value.key.startswith("mac_address"):
                    if macSetPairs is None: macSetPairs = {}
                    macSetPairs[value.key] = value.value
                else:
                    if hddsSetReq is None: hddsSetReq = SetReq()
                    hddsValue = hddsSetReq.values.add()
                    hddsValue.key = value.key
                    hddsValue.value = value.value

            if macSetPairs is not None: self.macSet(response, macSetPairs)
            if hddsSetReq is not None: self.hddsSet(response, hddsSetReq)
        else:
            self.log.error("Unexpected Request Type %d" % msg.body.requestType)

        return ThalesZMQMessage(response)

    def addResp(self, response, key="", value="", success=False):
        respVal = response.values.add()
        respVal.key = key
        respVal.value = value
        respVal.success = success

    def ifeGet(self, response, ifeReq):
        # IFE get messages are handled by the QTA running on the IFE VM
        ifeVmQtaResponse = self.ifeVmQtaClient.sendRequest(ifeReq)

        if ifeVmQtaResponse.name == "HostDomainDeviceServiceResponse":
            deserializedResponse = HostDomainDeviceServiceResponse()
            deserializedResponse.ParseFromString(ifeVmQtaResponse.serializedBody)
            response.values = deserializedResponse.values
        else:
            self.log.error("Unexpected response from IFE VM HDDS: %s" % ifeVmQtaResponse.name)
            self.addResp(response)

    def macGet(self, response, macKeys):
        for key in macKeys:
            target = key.split('.')[1]

            if target.startswith("processor"):
                self.addMacResp(response, key, self.cpuEthernetDev)
            elif target.startswith("i350"):
                self.addMacResp(response, key, self.i350EthernetDev + target[-1])
            else:
                self.log.warning("Invalid or not yet supported key: %s" % key)
                self.addResp(response, key)

    def addMacResp(self, response, key, device):
        mac = check_output(["cat", "/sys/class/net/%s/address" % device])

        if mac != "":
            self.addResp(response, key, mac, True)
        else:
            self.log.warning("Unable to retrieve MAC from: /sys/class/net/%s/address" % device)
            self.addResp(response, key)

    ## Handles incoming GET requests
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     value   HostDomainDeviceServiceRequest object
    def hddsGet(self, response, hddsReq):
        #  Just pass through to the actual HDDS service
        HDDSResp = self.hddsClient.sendRequest(ThalesZMQMessage(hddsReq))

        #  Check that we got back the expected response
        if HDDSResp.name == "GetResp":
            getResp = GetResp()
            getResp.ParseFromString(HDDSResp.serializedBody)

            for value in getResp.values:
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

    def macSet(self, response, macPairs):
        for key in macPairs:
            target = key.split('.')[1]
            
            if target.startswith("processor"):
                self.cpuMacSet(response, key, macPairs[key])
            else:
                self.log.warning("Invalid or not yet supported key: %s" % key)
                self.addResp(response, key, macPairs[key])

    def cpuMacSet(self, response, key, mac):

        bank = check_output(["mps_biostool", "get-active"])

        if bank != "":

        else:
            self.log.warning("Unable to get active BIOS bank.")
            self.addResp(response, key, macPairs[key])
        if bank !=

        if call(["mps_biostool", "set-mac", macPairs[key]]) == 0:
            if call(["mps_biostool", "set-active", "1"]) == 0:



    ## Handles incoming SET requests
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     request   HostDomainDeviceServiceRequest object
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
