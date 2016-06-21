
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.gpb.python.HDDS_pb2 import GetReq, GetResp, SetReq, SetResp
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
        self.hddsClient = ThalesZMQClient("tcp://localhost:40001")

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
        else:
            self.log.warning("Unexpected response from HDDS: %s" % response.name)
            # Since this module is a pass-through, return it anyway

        return response
