import os

from nms.host.pb2.nms_host_api_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


## VlanAssignment Module Class
#
class VlanAssignment(Module):
    ## Constructor
    #  @param       self
    #  @param       config - Configuration for the instance is going to be created
    def __init__(self, config=None):
        # Constructor of the parent class
        super(VlanAssignment, self).__init__(config)
        ## List of physical function names for validating the port name
        self.pfNames = ["i350_pf_1", "i350_pf_2", "i350_pf_3", "i350_pf_4"]
        ## List of virtual function names for validating the port name
        self.vfNames = ["vf1", "vf2", "vf3", "vf4", "vf5", "vf6", "vf7"]
        ## IP address of the device
        self.switchAddress = "10.10.41.159"
        self.loadConfig(attributes=('switchAddress'))
        # adding the message handler
        self.addMsgHandler(VLANAssignReq, self.hdlrMsg)

    ## Sets response fields
    #  @param   self
    #  @param   response    A VLANAssignResp object
    #  @param   success     Success flag to be added to respone
    #  @param   errCode     Optional error code for ErrorMessage field
    #  @param   errDesc     Optional error description text for ErrorMessage field
    def setResp(self, response, success=False, errCode=None, errDesc=""):
        response.success = success
        if errCode:
            self.log.error(errDesc)
            response.error.error_code = errCode
            response.error.error_description = errDesc

    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param:     self
    #  @param:     request           - tzmq format message
    #  @return:    ThalesZMQMessage  - Response object
    def hdlrMsg(self, request):
        # Create the empty response
        response = VLANAssignResp()
        response.success = True
        # Build a list of virtual functions to act on
        vfs = set()

        # If there is no port name, return an error
        if len(request.body.port_name) == 0:
            self.setResp(response, False, ERROR_PROCESSING_MESSAGE, "Empty port_name field")
        else:
            # Check that all port names are valid
            for port in request.body.port_name:
                if "_vf" not in port:
                    # Physical function
                    if port not in self.pfNames:
                        self.setResp(response, False, ERROR_PROCESSING_MESSAGE, "Invalid port name %s" % port)
                    else:
                        self.setResp(response, False, VLAN_ASSIGNMENT_FAILED, "PF configuration not yet supported")
                else:
                    # Virtual function
                    parts = port.rsplit('_', 1)
                    if len(parts) != 2 or parts[0] not in self.pfNames or parts[1] not in self.vfNames:
                        self.setResp(response, False, ERROR_PROCESSING_MESSAGE, "Invalid port name %s" % port)
                        break
                    vfs.add(int(parts[1][-1]) - 1)

        if response.success:
            # Build list of pairs to send to I350 driver.
            # Each pair is 0 for external or 1 for internal, followed by VLAN ID
            vlanConf = []
            for vlan in request.body.external_vlans:
                vlanConf.append("0 %u" % vlan)
            for vlan in request.body.internal_vlans:
                vlanConf.append("1 %u" % vlan)

            for vf in vfs:
                self.log.info("Configuring vf%d: %s" % (vf, " ".join(vlanConf)))
                procPath = "/proc/driver/igb/vf%dvlans" % vf
                if not os.path.exists(procPath):
                    self.setResp(response, False, VLAN_ASSIGNMENT_FAILED, "I350 driver does not support VF config")
                    break
                else:
                    with open(procPath, 'wb') as procFile:
                        procFile.write(" ".join(vlanConf) + '\n')

                # Read back VLAN conf from driver to verify
                if response.success:
                    readback = ""
                    with open(procPath, 'r') as procFile:
                        readback = procFile.read(256)
                    lines = readback.splitlines()
                    # Must be same number of lines and each line in vlanConf must be in the read back list
                    if len(lines) != len(vlanConf):
                        self.setResp(response, False, VLAN_ASSIGNMENT_FAILED, "I350 driver error configuring VF %d" % vf)
                    else:
                        for confLine in vlanConf:
                            if confLine not in lines:
                                self.setResp(response, False, VLAN_ASSIGNMENT_FAILED, "I350 driver error configuring VF %d" % vf)
                                break

                    if not response.success:
                        self.log.error("Read back vf%d: %s" % (vf, " ".join(lines)))

        return ThalesZMQMessage(response)
