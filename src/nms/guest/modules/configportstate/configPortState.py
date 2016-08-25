from operator import concat

from common.module.module import Module
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.vtss.vtss import Vtss
from nms.guest.modules.configportstate.configPortStateException import ConfigPortStateException
from nms.guest.pb2.nms_guest_api_pb2 import ConfigPortStateReq, ConfigPortStateResp, BPDUStates, ConfigPortState

## ConfigPortState Class Module
#
class PortStateConfig(Module):
    ## Constructor
    #  @param       self
    #  @param       config - Configuration for the instance is going to be created
    def __init__(self, config=None):
        # Constructor of the parent class
        super(PortStateConfig, self).__init__(config)
        # IP address of the device
        self.ip = "10.10.41.159"
        # path to the spec file
        self.spec_file_path = '../../../spec-file'
        #self.loadConfig(attributes=('vtssip'))
        # adding the message handler
        self.addMsgHandler(ConfigPortStateReq, self.hdlrMsg)


    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param:     self
    #  @param:     ConfigPortStateReq  - tzmq format message
    #  @return:    ThalesZMQMessage    - Response object
    def hdlrMsg(self, configPortStateReq):
        #  Create the empty response
        response = ConfigPortStateResp()
        #  For each config requested
        for config in configPortStateReq.body.state:
            self.configPort(configPortState=config)

        return ThalesZMQMessage(response)

    ## Set the Requested configuration
    #
    #  @param:  ConfigPortState     - state
    #  @return: ConfigPortStateResp - response
    def configPort(self, configPortState):
        #  Port name
        named_port = configPortState.namedPort

        #  State to be placed
        state = configPortState.state

        #  Create the Vtss object with the relative path where
        #  we'll always place the spec file to avoid multiple downloas
        vtss = Vtss(switchIP=self.ip, specFile='mps-vtss-spec-rpc.spec')

        #  Try to download the spec file if it doesn't exits
        vtss.downloadSpecFiles(path=self.spec_file_path)

        if state == BPDUStates.DISABLED:
            #  Call the RPC
            json_resp = vtss.callMethod(request=["port.config.set", '[{"ifindex":"%s", "Shutdown":"True"}]' % (named_port,)])
        elif state == BPDUStates.BLOCKING or state == BPDUStates.LEARNING or state == BPDUStates.FORWARDING or state == BPDUStates.LISTENING:
            #  Call the RPC
            json_resp = vtss.callMethod(request=["port.config.set", '[{"ifindex":"%s", "Shutdown":"True"}]' % (named_port,)])

        response = self.constructResponse(configPortState)

        return response

    ## Construct the response back, according to the request
    #
    #  @param:  ConfigPortState obj
    #  @return: ConfigPortStateResp obj
    def constructResponse(self, configPortState):
        response = ConfigPortStateResp()
        #  Set the name of the port
        response.state.namedPort = configPortState.namedPort
        #  Set the state
        vtss = Vtss(switchIP=self.ip, specFile='mps-vtss-spec-rpc.spec')
        jsonresp = vtss.callMethod(["mstp.status.interface.get"])
        response.state.state = 0



