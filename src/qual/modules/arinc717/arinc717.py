import os
from common.gpb.python.ARINC717Frame_pb2 import ARINC717FrameRequest, ARINC717FrameResponse
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.ARINC717Driver_pb2 import Request, Response, ChannelConfig
from common.gpb.python.GPIOManager_pb2 import RequestMessage, ResponseMessage
from common.module.module import Module

## ARINC717 Module
class ARINC717(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config =None):
        #  Initialize parent class
        super(ARINC717, self).__init__(config)

        #  Ensure directory for communication with ARINC717 driver is present
        ipcdir = "/tmp/arinc/driver/717"
        if not os.path.exists(ipcdir):
            os.makedirs(ipcdir)

        ## Connection to ARINC717 driver
        self.driverClient = ThalesZMQClient("ipc:///tmp/arinc/driver/717/device", log=self.log, msgParts=1, timeout=4000)
        #  Configure ARINC717 driver
        confReq = Request()
        confReq.type = Request.SET_CONFIG
        confReq.config.decoder = ChannelConfig.HBP
        confReq.config.rate = ChannelConfig.WPS_8192
        response = self.driverClient.sendRequest(ThalesZMQMessage(confReq))

        #  Parse the response from the config request
        if response.name == self.driverClient.defaultResponseName:
            confResp = Response()
            confResp.ParseFromString(response.serializedBody)
            self.log.info('\n%s' % confResp)

            if confResp.errorCode != Response.NONE:
                self.log.error("Error configuring ARINC717 driver")
                self.log.error("ERROR CODE: %s" % confResp.errorCode)

        # Additional configuration: Set GPIO pin low to enable HBP mode.
        # The ARINC-717 driver really should do this, but it does not do it currently.
        # If the driver is updated to do this, we can remove it from here.
        gpioMgrClient = ThalesZMQClient("ipc:///tmp/gpio-mgr.sock", log=self.log, msgParts=1)
        setReq = RequestMessage()
        setReq.pin_name = "RxLineSelect_717"
        setReq.request_type = RequestMessage.SET
        setReq.value = 0
        response = gpioMgrClient.sendRequest(ThalesZMQMessage(setReq))

        # Parse the response from the GPIO request
        if response.name == gpioMgrClient.defaultResponseName:
            setResp = ResponseMessage()
            setResp.ParseFromString(response.serializedBody)
            if setResp.error != ResponseMessage.OK:
                self.log.error("Error return from GPIO Manager")
                self.log.error("ERROR CODE: %s" % setResp.error)

        #  Add handler to available message handlers
        self.addMsgHandler(ARINC717FrameRequest, self.handler)

    ## Sends RECEIVE_FRAME request message to the ARINC717 driver
    #  @param     self
    #  @return    a ThalesZMQMessage object returned from the ARINC717 driver
    def makeDriverRequest(self):
        request = Request()
        request.type = Request.RECEIVE_FRAME

        return self.driverClient.sendRequest(ThalesZMQMessage(request))

    ## Handles incoming messages
    #  Receives TZMQ request and performs requested action
    #  @param     self
    #  @param     msg       TZMQ format message
    #  @return    a ThalesZMQMessage object containing the response message
    def handler(self, msg):
        response = ARINC717FrameResponse()
        response.state = ARINC717FrameResponse.RUNNING
        response.syncState = ARINC717FrameResponse.NO_SYNC

        if msg.body.requestType == ARINC717FrameRequest.RUN:
            self.start(response)
        elif msg.body.requestType == ARINC717FrameRequest.STOP:
            self.stop(response)
        elif msg.body.requestType == ARINC717FrameRequest.REPORT:
            self.report(response)
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        return ThalesZMQMessage(response)

    ## Handles messages with requestType of RUN
    #  RUN request type is defined in the ICD, but is not applicable to
    #  this module, so we just behave the same as REPORT.
    #  @param     self
    #  @param     response  an ARINC717FrameResponse object to be returned to the caller
    def start(self, response):
        self.report(response)

    ## Handles messages with requestType of STOP
    #  STOP request type is defined in the ICD, but is not applicable to
    #  this module, so we just behave the same as REPORT.
    #  @param     self
    #  @param     response  an ARINC717FrameResponse object to be returned to the caller
    def stop(self, response):
        self.report(response)

    ## Handles messages with requestType of REPORT
    #  @param     self
    #  @param     response  an ARINC717FrameResponse object to be returned to the caller
    def report(self, response):
        driverResponse = self.makeDriverRequest()
        if driverResponse.name == self.driverClient.defaultResponseName:
            info = Response()
            info.ParseFromString(driverResponse.serializedBody)
            self.log.info('\n%s' % info)
            data = info.frame.data
            response.syncState = ARINC717FrameResponse.NO_SYNC if info.frame.out_of_sync else ARINC717FrameResponse.SYNCED

            #  turns every two characters in data into 16-bit data
            for char in range(0, len(data), 2):
                response.arinc717frame.append((ord(data[char]) << 8) | ord(data[char + 1]))
        else:
            #  Not documented but since we have the field let's use it:
            #  If we can't contact the driver, return the state as "STOPPED"
            response.state = ARINC717FrameResponse.STOPPED
