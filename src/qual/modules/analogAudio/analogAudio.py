from qual.pb2.AnalogAudio_pb2 import AnalogAudioRequest, AnalogAudioResponse
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


## AnalogAudio Module Class
class AnalogAudio(Module):
    ## Constructor
    #  @param   self
    #  @param   config          Configuration for this module instance
    def __init__(self, config=None):
        #  Initializes parent class
        super(AnalogAudio, self).__init__(config)
        ## Address for communicating with QTA running on the IFE VM
        self.ifeVmQtaAddr = "tcp://localhost:50003"
        self.loadConfig(attributes=('ifeVmQtaAddr',))
        ## Connection to QTA running on the IFE VM
        self.ifeVmQtaClient = ThalesZMQClient(self.ifeVmQtaAddr, log=self.log, timeout=4000)
        #  Add handler to available message handlers
        self.addMsgHandler(AnalogAudioRequest, self.handler)

    ## Handles incoming messages
    #  Receives tzmq request and passes it to the QTA running on the IFE VM
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  AnalogAudioResponse object
    def handler(self, msg):
        if msg.body.requestType == AnalogAudioRequest.CONNECT:
            self.log.info("AnalogAudio - connect %s %s" % (msg.body.source, msg.body.sink))
        elif msg.body.requestType == AnalogAudioRequest.DISCONNECT:
            self.log.info("AnalogAudio - disconnect %s" % msg.body.sink)
        else:
            self.log.debug("AnalogAudio - report %s" % msg.body.sink)

        ifeVmQtaResponse = self.ifeVmQtaClient.sendRequest(msg)

        if ifeVmQtaResponse.name == "AnalogAudioResponse":
            deserializedResponse = AnalogAudioResponse()
            deserializedResponse.ParseFromString(ifeVmQtaResponse.serializedBody)
            ifeVmQtaResponse.body = deserializedResponse
            self.log.debug("AnalogAudio - returning response")
            return ifeVmQtaResponse
        else:
            self.log.error("Unexpected response from IFE VM AnalogAudio: %s" % ifeVmQtaResponse.name)

        return ThalesZMQMessage(AnalogAudioResponse())
