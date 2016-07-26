from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.HDDS_pb2 import HostDomainDeviceServiceRequest, HostDomainDeviceServiceResponse
from common.gpb.python.HDDS_API_pb2 import GetReq, GetResp, SetReq, SetResp
from common.gpb.python.ErrorMessage_pb2 import ErrorMessage
from common.module.module import Module

## HDDS Module
class HDDS(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        #  Initialize parent class
        super(HDDS, self).__init__(config)
        ## Client connection to the Host Domain Device Service
        self.hddsClient = ThalesZMQClient("tcp://localhost:40001", log=self.log)
        #  Add handler to available message handlers
        self.addMsgHandler(HostDomainDeviceServiceRequest, self.handler)

    ## Handles incoming messages
    #  Receives tzmq request and runs requested process
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  ThalesZMQMessage object
    def handler(self, msg):
        response = HostDomainDeviceServiceResponse()
        response.key = msg.body.key

        if msg.body.requestType == HostDomainDeviceServiceRequest.GET:
            self.getHandler(response, msg.body)
        elif msg.body.requestType == HostDomainDeviceServiceRequest.SET:
            self.setHandler(response, msg.body)
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        return ThalesZMQMessage(response)

    ## Handles incoming GET requests
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    def getHandler(self, response, request):
        getReq = GetReq()
        getReq.key.append(request.key)
        # Just pass through to the actual HDDS service
        HDDSResp = self.hddsClient.sendRequest(ThalesZMQMessage(getReq))

        # Check that we got back the expected response and deserialize for debugging purposes
        if HDDSResp.name == "GetResp":
            getResp = GetResp()
            getResp.ParseFromString(HDDSResp.serializedBody)
            response.success = getResp.success
            response.value = getResp.values[0].keyValue.value
        else:
            response.success = False
            response.value = ""

            if HDDSResp.name == "ErrorMessage":
                err = ErrorMessage()
                err.ParseFromString(HDDSResp.serializedBody)
                self.log.warning("Got error message from HDDS: %s" % err.error_description)
            elif HDDSResp.name == "":
                self.log.warning("Get failed: No response from HDDS")
            else:
                self.log.warning("Unexpected response from HDDS: %s" % HDDSResp.name)

    ## Handles incoming SET requests
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     value     Value to set key to
    def setHandler(self, response, request):
        setReq = SetReq()
        req = setReq.values.add()
        req.key = request.key
        req.value = request.value
        # Just pass through to the actual HDDS service
        HDDSResp = self.hddsClient.sendRequest(ThalesZMQMessage(setReq))

        # Check that we got back the expected response and deserialize for debugging purposes
        if HDDSResp.name == "SetResp":
            setResp = SetResp()
            setResp.ParseFromString(HDDSResp.serializedBody)
            response.success = setResp.success
            response.value = setResp.values[0].keyValue.value if setResp.success else ""
        else:
            response.success = False
            response.value = ""

            if HDDSResp.name == "ErrorMessage":
                err = ErrorMessage()
                err.ParseFromString(HDDSResp.serializedBody)
                self.log.warning("Got error message from HDDS: %s" % err.error_description)
            elif response.name == "":
                self.log.warning("Set failed: No response from HDDS")
            else:
                self.log.warning("Unexpected response from HDDS: %s" % HDDSResp.name)