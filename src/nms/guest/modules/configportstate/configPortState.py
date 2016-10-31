from nms.common.portresolver.portResolver import resolvePort, updatePorts
from nms.guest.pb2.nms_guest_api_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.vtss.vtss import Vtss


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
        self.switchAddress = "10.10.41.159"
        # path to the spec file
        self.spec_file_path = '/tmp'
        self.loadConfig(attributes=('switchAddress',))
        # adding the message handler
        self.addMsgHandler(ConfigPortStateReq, self.hdlrMsg)
        # Update the enet_8 and i350 port names
        updatePorts(self)


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
            bpduPortState = response.state.add()
            # Get the responses in an aux variable
            aux = self.configPort(configPortState=config)
            # Copy the results
            bpduPortState.namedPort        = aux.namedPort
            bpduPortState.state            = aux.state
            bpduPortState.success          = aux.success
            bpduPortState.error.error_code = aux.error.error_code

        return ThalesZMQMessage(response)

    ## Set the Requested configuration
    #
    #  @param:  ConfigPortState     - state
    #  @return: ConfigPortStateResp - response
    def configPort(self, configPortState):
        bpduPortState = BPDUPortState()
        #  Port name
        switchPortName= resolvePort(configPortState.namedPort)

        #  Create the Vtss object with the relative path where
        #  we'll always place the spec file to avoid multiple downloas
        vtss = Vtss(switchIP=self.switchAddress, specFile='mps-vtss-spec-rpc.spec')

        #  Try to download the spec file if it doesn't exits
        vtss.downloadSpecFiles(path=self.spec_file_path)

        #  if port name doesn't exist or it's not a switch port, return error
        if switchPortName != None and switchPortName[1]:
            #  State to be placed
            state = configPortState.state

            if state == DISABLED:
                #  Call the RPC
                jsonResp = vtss.callMethod(request=["port.config.set", "%s" % (switchPortName[0],), '{"Shutdown":true}'])
            elif state == BLOCKING or state == LEARNING or state == FORWARDING or state == LISTENING:
                #  Call the RPC
                jsonResp = vtss.callMethod(request=["port.config.set", "%s" % (switchPortName[0],), '{"Shutdown":false}'])
            else:
                ## Invalid Message received
                #  Set the port name in the response
                bpduPortState.namedPort = configPortState.namedPort
                #  Set the current port state
                jsonPortState = vtss.callMethod(request=["mstp.status.interface.get", "%s" % (switchPortName[0],), 0])
                bpduPortState.state = self.resolveState(jsonPortState['result']['PortState'])
                #  Success is False
                bpduPortState.success = False
                #  Eror 1004: Invalid Message Received
                bpduPortState.error.error_code = 1004

                return bpduPortState

            # Now that we did the work let's create the response
            if jsonResp['error'] != None:
                #  Set the port name in the response
                bpduPortState.namedPort = configPortState.namedPort
                #  Set the current port state
                jsonPortState = vtss.callMethod(request=["mstp.status.interface.get", "%s" % (switchPortName[0],), 0])
                bpduPortState.state = self.resolveState(jsonPortState['result']['PortState'])
                #  Success is False
                bpduPortState.success = False
                #  Eror 1005: Error Processing Message
                bpduPortState.error.error_code = 1005
            else:
                #  Set the port name in the response
                bpduPortState.namedPort = configPortState.namedPort
                #  Set the current port state
                jsonPortState = vtss.callMethod(request=["mstp.status.interface.get", "%s" % (switchPortName[0],), 0])
                bpduPortState.state = self.resolveState(jsonPortState['result']['PortState'])
                #  Success is True
                bpduPortState.success = True

        # If the name Doesn't exists, return error code 1003
        elif switchPortName == None:
            #  Set the port name in the response
            bpduPortState.namedPort = configPortState.namedPort
            #  Set the current port state
            bpduPortState.state = DISABLED
            #  Success is False
            bpduPortState.success = False
            #  Eror 1003: Port name does not exist in this setup
            bpduPortState.error.error_code = 1003
        else:
            # Here, port name but doesn't belong to the switch
            #  Set the port name in the response
            bpduPortState.namedPort = configPortState.namedPort
            #  Set the current port state
            bpduPortState.state = DISABLED
            #  Success is False
            bpduPortState.success = False
            #  Eror 1001: Port is not supported in this setup
            bpduPortState.error.error_code = 1001

        return bpduPortState

    ## This function maps the port states according with the ICD
    #
    #  @type:   str
    #  @param:  string with the port state response from the switch.
    #  @return: port state according to the ICD
    def resolveState(self, strState):
        if strState == 'forwarding':
            return FORWARDING
        elif strState == 'disabled':
            return DISABLED
        elif strState == 'discarding':
            return BLOCKING
        elif strState == 'learning':
            return LEARNING
        else:
            # We shouldn't get here
            return None





