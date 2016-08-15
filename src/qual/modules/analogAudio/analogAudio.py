from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.AnalogAudio_pb2 import AnalogAudioRequest, AnalogAudioResponse
from common.module.module import Module

## AnalogAudio Module Class
class AnalogAudio(Module):
    ## Constructor
    #  @param   self
    #  @param   config          Configuration for this module instance
    #  @param   deserialize     Flag to deserialize the responses when running unit test
    def __init__(self, config=None, deserialize=False):
        #  Initializes parent class
        super(AnalogAudio, self).__init__(config)
        ## Address for communicating with QTA running on the IFE VM
        self.ifeVmQtaAddr = "tcp://localhost:50003"
        self.loadConfig(attributes=('ifeVmQtaAddr',))
        ## Connection to QTA running on the IFE VM
        self.ifeVmQtaClient = ThalesZMQClient(self.ifeVmQtaAddr, log=self.log, timeout=4000)
        ## Flag for unit test to deserialize responses
        self.deserialize = deserialize
        #  Add handler to available message handlers
        self.addMsgHandler(AnalogAudioRequest, self.handler)

    ## Handles incoming messages
    #  Receives tzmq request and passes it to the QTA running on the IFE VM
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  AnalogAudioResponse object
    def handler(self, msg):
        ifeVmQtaResponse = self.ifeVmQtaClient.sendRequest(msg)

        if ifeVmQtaResponse.name == "AnalogAudioResponse":
            deserializedResponse = AnalogAudioResponse()
            deserializedResponse.ParseFromString(ifeVmQtaResponse.serializedBody)
            ifeVmQtaResponse.body = deserializedResponse
            return ifeVmQtaResponse
        else:
            self.log.error("Unexpected response from IFE VM AnalogAudio: %s" % ifeVmQtaResponse.name)

        return ThalesZMQMessage(AnalogAudioResponse())
