from datetime import datetime
from common.pb2.rtc_driver_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.pb2.RTC_pb2 import *
import subprocess



## RTC Module class
#   Passes through the RTC message
class Rtc(Module):
    ## Constructor
    def __init__(self):
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
        # Request: RTC_GET
        if rtcRequest.body.requestType == RTCRequest.RTC_GET:
            rtcResponse = self.rtcGet()
        # Request: RTC_SET
        elif rtcRequest.body.requestType == RTCRequest.RTC_SET:
            rtcResponse = self.rtcSet(rtcRequest.body.timeString)
        # Request: SYSTEM_TO_RTC
        elif rtcRequest.body.requestType == RTCRequest.SYSTEM_TO_RTC:
            rtcResponse = self.rtcSet(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ'))
        # Request: RTC_TO_SYSTEM
        elif rtcRequest.body.requestType == RTCRequest.RTC_TO_SYSTEM:
            response = self.rtcGet()
            # succeeded???
            if response.success:
                # Set the system date time
                if subprocess.call(['date', '-s', response.timeString], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                    rtcResponse.success = True
                else:
                    rtcResponse.success = False
            else:
                rtcResponse = response
        # Request: RTC_SYSTEM_SET
        elif rtcRequest.body.requestType == RTCRequest.RTC_SYSTEM_SET:
            # first set the RTC
            rtcResponse = self.rtcSet(rtcRequest.body.timeString)
            # Succeeded???
            if rtcResponse.success:
                # Set the system date time
                if subprocess.call(['date', '-s', rtcRequest.body.timeString], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                    rtcResponse.success = True
                else:
                    rtcResponse.success = False
        # Request: UNKNOWN
        else:
            self.log.error("Invalid RTC request: %d" % rtcRequest.body.requestType)
            rtcResponse.success = False

        return ThalesZMQMessage(rtcResponse)

    ## Requests: RTC_GET
    #
    def rtcGet(self):
        # Create the empty response
        rtcResponse = RTCResponse()
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
                rtcResponse.success = False
        else:
            self.log.error("Unexpected response from RTC: %s" % response.name)
            rtcResponse.success = False

        return rtcResponse

    ## Requests: RTC_SET
    #
    def rtcSet(self, timeString):
        # Create the empty response
        rtcResponse = RTCResponse()
        # Object to deserialize the response
        timeResponse = TimeResponse()
        # Create the Set Time obj
        setTime = SetTime()
        setTime.datetime = timeString
        # Pass the message to the RTC Driver/Simulator
        response = self.rtcThalesZMQClient.sendRequest(ThalesZMQMessage(setTime))
        time = self.rtcThalesZMQClient.sendRequest(ThalesZMQMessage(GetTime()))
        # Deserialize the response
        if response.name == "TimeResponse":
            timeResponse.ParseFromString(response.serializedBody)
            if timeResponse.error == SUCCESS:
                rtcResponse.success = True
                # now, the RTC time
                if time.name == "TimeResponse":
                    # succeeded???
                    if timeResponse.error == SUCCESS:
                        rtcResponse.success = True
                        rtcResponse.timeString = timeResponse.datetime
                    else:
                        rtcResponse.success = False
                else:
                    self.log.error("Unexpected response from RTC: %s" % response.name)
                    rtcResponse.success = False
            else:
                rtcResponse.success = False
        else:
            self.log.error("Unexpected response from RTC: %s" % response.name)
            rtcResponse.success = False

        return rtcResponse