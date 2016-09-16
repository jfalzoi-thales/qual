import os
from datetime import datetime
from common.pb2.rtc_driver_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.pb2.RTC_pb2 import *
import subprocess

## Discard the output
DEVNULL = open(os.devnull, 'wb')

## RTC Module class
#   Passes through the RTC message
class Rtc(Module):
    ## Constructor
    def __init__(self, config=None):
        # Init the parent class
        super(Rtc, self).__init__(None)
        # Init the ThalesZMQClient
        # per the "MAP Network Configuration" document.
        self.rtcThalesZMQClient = ThalesZMQClient(address="ipc:///tmp/rtc-drv.sock", log=self.log, msgParts=2)
        # adding the message handler
        self.addMsgHandler(RTCRequest, self.handlerRequestMessage)

    ## Called by base class when an RTCRequest object is received from a client.
    #
    #  @param: RTC Request
    #  @type:  RTCRequest obj
    def handlerRequestMessage(self,rtcRequest):
        # Create the empty response
        rtcResponse = RTCResponse()
        rtcResponse.success = False
        rtcResponse.timeString = ''
        # Request: RTC_GET
        if rtcRequest.body.requestType == RTCRequest.RTC_GET:
            rtcResponse = self.rtcGet()
        # Request: RTC_SET
        elif rtcRequest.body.requestType == RTCRequest.RTC_SET:
            rtcResponse = self.rtcSet(rtcRequest.body.timeString)
        else:
            rtcResponse.errorMessage = "Invalid RTC request: %d" % rtcRequest.body.requestType
            self.log.error("Invalid RTC request: %d" % rtcRequest.body.requestType)

        return ThalesZMQMessage(rtcResponse)

    ## Requests: RTC_GET
    #
    def rtcGet(self):
        # Create the empty response
        rtcResponse = RTCResponse()
        rtcResponse.success = False
        rtcResponse.timeString = ''
        # Object to deserialize the response
        timeResponse = TimeResponse()
        # Pass the message to the RTC Driver/Simulator
        response = self.rtcThalesZMQClient.sendRequest(ThalesZMQMessage(GetTime()))
        # Deserialize the response
        if response.name == "TimeResponse":
            timeResponse.ParseFromString(response.serializedBody)
            if timeResponse.error == SUCCESS:
                rtcResponse.success = True
                rtcResponse.timeString = timeResponse.datetime
            else:
                rtcResponse.errorMessage = "Error retrieving time from RTC: Error code %s" % timeResponse.error
                self.log.error("Error retrieving time from RTC: Error code %s" % timeResponse.error)
        else:
            rtcResponse.errorMessage = "Unexpected response from RTC: %s" % response.name
            self.log.error("Unexpected response from RTC: %s" % response.name)

        return rtcResponse

    ## Requests: RTC_SET
    #
    def rtcSet(self, timeString):
        # Create the empty response
        rtcResponse = RTCResponse()
        rtcResponse.success = False
        rtcResponse.timeString = ''
        # Object to deserialize the response
        timeResponse = TimeResponse()
        # Create the Set Time obj
        setTime = SetTime()
        setTime.datetime = timeString
        # Pass the message to the RTC Driver/Simulator
        setTimeResponse = self.rtcThalesZMQClient.sendRequest(ThalesZMQMessage(setTime))
        getTimeResponse = self.rtcThalesZMQClient.sendRequest(ThalesZMQMessage(GetTime()))
        # Deserialize the response
        if setTimeResponse.name == "TimeResponse":
            timeResponse.ParseFromString(setTimeResponse.serializedBody)
            if timeResponse.error == SUCCESS:
                # now, the RTC time
                if getTimeResponse.name == "TimeResponse":
                    timeResponse.ParseFromString(getTimeResponse.serializedBody)
                    # succeeded???
                    if timeResponse.error == SUCCESS:
                        rtcResponse.success = True
                        rtcResponse.timeString = timeResponse.datetime
                    else:
                        rtcResponse.errorMessage = "Error retrieving time from RTC: Error code %s" % timeResponse.error
                        self.log.error("Error retrieving time from RTC: Error code %s" % timeResponse.error)
                else:
                    rtcResponse.errorMessage = "Unexpected response from RTC: %s" % getTimeResponse.name
                    self.log.error("Unexpected response from RTC: %s" % getTimeResponse.name)
            else:
                rtcResponse.errorMessage = "Error setting time on RTC: Error code %s" % timeResponse.error
                self.log.error("Error setting time on RTC: Error code %s" % timeResponse.error)
        else:
            rtcResponse.errorMessage = "Unexpected response from RTC: %s" % setTimeResponse.name
            self.log.error("Unexpected response from RTC: %s" % setTimeResponse.name)

        return rtcResponse