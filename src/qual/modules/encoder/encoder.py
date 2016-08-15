from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.gpb.python.Encoder_pb2 import EncoderRequest, EncoderResponse
from common.module.module import Module

## Video Encoder Module Class
class Encoder(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None, deserialize=False):
        #  Initializes parent class
        super(Encoder, self).__init__(config)
        ## Address for communicating with QTA running on the IFE VM
        self.ifeVmQtaAddr = "tcp://localhost:50003"
        self.loadConfig(attributes=('ifeVmQtaAddr',))
        ## Connection to QTA running on the IFE VM
        self.ifeVmQtaClient = ThalesZMQClient(self.ifeVmQtaAddr, log=self.log)
        ## Flag for unit test to deserialize responses
        self.deserialize = deserialize
        #  Add handler to available message handlers
        self.addMsgHandler(EncoderRequest, self.handler)


    ## Handles incoming messages
    #  Receives tzmq request and passes it to the QTA running on the IFE VM
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  EncoderResponse object
    def handler(self, msg):
        ifeVmQtaResponse = self.ifeVmQtaClient.sendRequest(msg)

        if ifeVmQtaResponse.name == "EncoderResponse":
            if self.deserialize:
                deserializedResponse = EncoderResponse()
                deserializedResponse.ParseFromString(ifeVmQtaResponse.serializedBody)
                ifeVmQtaResponse.body = deserializedResponse

            return ifeVmQtaResponse
        else:
            self.log.error("Unexpected response from IFE VM Encoder: %s" % ifeVmQtaResponse.name)

        response = EncoderResponse()
        response.state = EncoderResponse.STOPPED
        response.streamActive = False

        return ThalesZMQMessage(response)