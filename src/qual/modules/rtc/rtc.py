from common.pb2.rtc_driver_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage



## RTC Module class
#   Passes through the RTC message
class Rtc(Module):
    ## Constructor
    def __init__(self):
        # Init the parent class
        super(Rtc, self).__init__(None)
        # Init the ThalesZMQClient
        # per the "MAP Network Configuration" document.
        self.thalesZMQClient = ThalesZMQClient(address="ipc:///tmp/rtc-drv.sock", log=self.log, msgParts=2)
        # adding the message handler
        self.addMsgHandler(GetTime, self.handlerMessage)
        self.addMsgHandler(SetTime, self.handlerMessage)

    ## Called by base class when a request is received from a client.
    #
    #  @param request ThalesZMQMessage object containing received request
    def handlerMessage(self, thalesZMQMessage):
        # Log the message request
        self.log.info('Message received: %s' % thalesZMQMessage.name)
        deserializedResponse = TimeResponse()
        # Pass the message to the RTC Driver/Simulator
        response =  self.thalesZMQClient.sendRequest(thalesZMQMessage)
        # Deserialize the response
        if response.name == "TimeResponse":
            deserializedResponse.ParseFromString(response.serializedBody)
            response.body = deserializedResponse

            return response
        else:
            self.log.error("Unexpected response from RTC: %s" % response.name)
            # Return an RTC error
            deserializedResponse.error = RTC_ERROR

            return ThalesZMQMessage(deserializedResponse)
