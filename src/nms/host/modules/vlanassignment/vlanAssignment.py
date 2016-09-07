from tklabs_utils.vtss.portResolver import resolvePort
from nms.host.pb2.nms_host_api_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.vtss.vtss import Vtss


## VlanAssignment Class Module
#
class VlanAssignment(Module):
    ## Constructor
    #  @param       self
    #  @param       config - Configuration for the instance is going to be created
    def __init__(self, config=None):
        # Constructor of the parent class
        super(VlanAssignment, self).__init__(config)
        # List of port names
        self.portNames = ['internal.i350_pf_%s' % (x,) for x in range(1, 5)] + ['internal.i350_vf_%s' % (x,) for x in range(1, 29)]
        # IP address of the device
        self.switchAddress = "10.10.41.159"
        self.loadConfig(attributes=('switchAddress'))
        # adding the message handler
        self.addMsgHandler(VLANAssignReq, self.hdlrMsg)


    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param:     self
    #  @param:     VlanAssigReq      - tzmq format message
    #  @return:    ThalesZMQMessage  - Response object
    def hdlrMsg(self, vlanAssigReq):
        #  Create the empty response
        response = VLANAssignResp()
        # If there is no port name, should return an error
        if len(vlanAssigReq.body.port_name) == 0:
            # Set success failed
            response.success = False
            # Error code 1002: Error Processing Message
            response.error.error_code = 1002
        else:
            # TODO: For each port name requested, make it part of each VLANs list

            # for now, let's just make it pass
            response.success = True

        return ThalesZMQMessage(response)
