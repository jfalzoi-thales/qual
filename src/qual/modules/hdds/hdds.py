
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.HDDS_pb2 import GetReq, GetResp, SetReq, SetResp, FAILURE_GET_FAILED
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

        #  Add handlers to available message handlers
        self.addMsgHandler(GetReq, self.getHandler)
        self.addMsgHandler(SetReq, self.setHandler)

    ## Handles incoming GetReq messages
    #  Receives TZMQ request and performs requested action
    #  @param     self
    #  @param     msg       TZMQ format message
    #  @return    a ThalesZMQMessage object containing the response message
    def getHandler(self, msg):
        # Just pass through to the actual HDDS service
        response = self.hddsClient.sendRequest(msg)

        # Check that we got back the expected response and deserialize for debugging purposes
        if response.name == "GetResp":
            getResp = GetResp()
            getResp.ParseFromString(response.serializedBody)
            response.body = getResp
        elif response.name == "ErrorMessage":
            err = ErrorMessage()
            err.ParseFromString(response.serializedBody)
            response.body = err
            self.log.warning("Got error message from HDDS: %s" % err.error_description)
        elif response.name == "":
            # Construct new response to report failure
            getResp = GetResp()
            valueResp = getResp.HDDSValue.add()
            valueResp.success = False
            valueResp.error.error_code = FAILURE_GET_FAILED
            valueResp.error.description = "Get failed: No response from HDDS"
            response = ThalesZMQMessage(getResp)
        else:
            self.log.warning("Unexpected response from HDDS: %s" % response.name)
            # Since this module is a pass-through, return it anyway

        return response

    ## Handles incoming SetReq messages
    #  Receives TZMQ request and performs requested action
    #  @param     self
    #  @param     msg       TZMQ format message
    #  @return    a ThalesZMQMessage object containing the response message
    def setHandler(self, msg):
        # Just pass through to the actual HDDS service
        response = self.hddsClient.sendRequest(msg)

        # Check that we got back the expected response and deserialize for debugging purposes
        if response.name == "SetResp":
            setResp = SetResp()
            setResp.ParseFromString(response.serializedBody)
            response.body = setResp
        elif response.name == "ErrorMessage":
            err = ErrorMessage()
            err.ParseFromString(response.serializedBody)
            response.body = err
            self.log.warning("Got error message from HDDS: %s" % err.error_description)
        elif response.name == "":
            # Construct new response to report failure
            setResp = SetResp()
            valueResp = setResp.HDDSValue.add()
            valueResp.success = False
            valueResp.error.error_code = FAILURE_GET_FAILED
            valueResp.error.description = "Set failed: No response from HDDS"
            response = ThalesZMQMessage(setResp)
        else:
            self.log.warning("Unexpected response from HDDS: %s" % response.name)
            # Since this module is a pass-through, return it anyway

        return response
