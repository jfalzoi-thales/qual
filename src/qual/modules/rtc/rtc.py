from common.pb2.rtc_driver_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient


## RTC Module class
#   Passes through the RTC message
class Rtc(Module):
    ## Constructor
    def __init__(self):
        # Init the parent class
        super(Rtc, self).__init__(None)
        # Init the ThalesZMQClient
        # per the "MAP Network Configuration" document.
        # TODO: On target system this needs to be 'ipc:///tmp/rtc-drv.sock'
        self.thalesZMQClient = ThalesZMQClient(address="tcp://localhost:40001", log=self.log)
        # adding the message handler
        self.addMsgHandler(GetTime, self.handlerMessage)
        self.addMsgHandler(SetTime, self.handlerMessage)

    ## Called by base class when a request is received from a client.
    #
    #  @param request ThalesZMQMessage object containing received request
    def handlerMessage(self, thalesZMQMessage):
        # Log the message request
        self.log.info('Message received: %s' % thalesZMQMessage.name)
        # Pass the message to the RTC Driver/Simulator
        return self.thalesZMQClient.sendRequest(thalesZMQMessage)