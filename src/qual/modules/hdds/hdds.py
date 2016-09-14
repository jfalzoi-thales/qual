import subprocess
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
            for value in msg.body.values:
                if value.key.startswith(("ife.voltage", "ife.temperature")):
                    if ifeGetReq == None: ifeGetReq = HostDomainDeviceServiceRequest()
                    ifeGetReq.requestType = HostDomainDeviceServiceRequest.GET
                    ifeValue = ifeGetReq.values.add()
                    ifeValue.key = value.key
                elif value.key.startswith("mac_address"):
                    if macGetKeys == None: macGetKeys = []
                    macGetKeys.append(value.key)
                else:
                    if hddsGetReq == None: hddsGetReq = GetReq()
                    hddsGetReq.key.append(value.key)

            if ifeGetReq != None: self.ifeGet(response, ifeGetReq)
            if macGetKeys != None: self.macGet(response, macGetKeys)
            if hddsGetReq != None: self.hddsGet(response, hddsGetReq)
        elif msg.body.requestType == HostDomainDeviceServiceRequest.SET:
            for value in msg.body.values:
                if value.key.startswith(("ife.voltage", "ife.temperature")):
                    self.log.warning("Attempted to set ife voltage or temperature.  Nothing to do.")
                    self.addResp(response, value.key)
                elif value.key.startswith("mac_address"):
                    if macSetPairs == None: macSetPairs = {}
                    macSetPairs[value.key] = value.value
                else:
                    if hddsSetReq == None: hddsSetReq = SetReq()
                    hddsValue = hddsSetReq.values.add()
                    hddsValue.key = value.key
                    hddsValue.value = value.value

            if macSetPairs != None: self.macSet(response, macSetPairs)
            if hddsSetReq != None: self.hddsSet(response, hddsSetReq)
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
                #parse ip addr
            elif target.startswith("i350"):
                #parse ip addr
            else:
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
        #  DO STUFF TO SET TEH MAC
        for pair in macPairs:
            self.addResp(response, pair, macPairs[pair])

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
