from nms.host.pb2.nms_host_api_pb2 import SwitchInfoReq, SwitchInfoResp
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.vtss.vtss import Vtss


## SwitchInfo Module Class
class SwitchInfo(Module):
    ## Constructor
    #  @param       self
    #  @param       config - Configuration for the instance is going to be created
    def __init__(self, config=None):
        # Constructor of the parent class
        super(SwitchInfo, self).__init__(config)
        ## IP address of the device
        self.switchAddress = "10.10.41.159"
        # Load config file
        self.loadConfig(attributes=('switchAddress',))
        # Add the message handler
        self.addMsgHandler(SwitchInfoReq, self.handleMsg)

    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param:    self
    #  @param     msg       TZMQ format message
    #  @return    a ThalesZMQMessage object containing the response message
    def handleMsg(self, msg):
        #  Create the response with simulated values
        response = SwitchInfoResp()
        response.success = True
        prop = response.values.add()
        prop.key = "temperature"
        prop.value = "30.0"

        return ThalesZMQMessage(response)
