import os

from common.pb2.ARINC717Driver_pb2 import Request, Response, ChannelConfig
from common.pb2.GPIOManager_pb2 import RequestMessage, ResponseMessage
from qual.pb2.ARINC717Frame_pb2 import ARINC717FrameRequest, ARINC717FrameResponse
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


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

        ##  Indicates if state is running
        self.running = False
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
        response.syncState = ARINC717FrameResponse.NO_SYNC

        if msg.body.requestType in [ARINC717FrameRequest.STOP, ARINC717FrameRequest.RUN, ARINC717FrameRequest.REPORT]:
            if msg.body.requestType == ARINC717FrameRequest.RUN: self.running = True

            if self.running:
                driverResponse = self.makeDriverRequest()

                if driverResponse.name == self.driverClient.defaultResponseName:
                    info = Response()
                    info.ParseFromString(driverResponse.serializedBody)
                    data = info.frame.data
                    if not info.frame.out_of_sync: response.syncState = ARINC717FrameResponse.SYNCED

                    #  turns every two characters in data into 16-bit data
                    for char in range(0, len(data), 2):
                        response.arinc717frame.append((ord(data[char]) << 8) | ord(data[char + 1]))
                else:
                    self.log.error("Unexpected Response Name: %s" % driverResponse.name)
                    if msg.body.requestType == ARINC717FrameRequest.RUN: self.running = False

            if msg.body.requestType == ARINC717FrameRequest.STOP: self.running = False
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        response.state = ARINC717FrameResponse.RUNNING if self.running else ARINC717FrameResponse.STOPPED

        return ThalesZMQMessage(response)
