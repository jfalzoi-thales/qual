from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.ARINC485_pb2 import ARINC485Request, ARINC485Response
from common.module.module import Module

## ARINC485 Module Class
class ARINC485(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        #  Initializes parent class
        super(ARINC485, self).__init__(config)
        ## Address for communicating with QTA running on the IFE VM
        self.ifeVmQtaAddr = "tcp://localhost:50003"
        self.loadConfig(attributes=('ifeVmQtaAddr',))
        ## Connection to QTA running on the IFE VM
        self.ifeVmQtaClient = ThalesZMQClient(self.ifeVmQtaAddr, log=self.log)
        #  Add handler to available message handlers
        self.addMsgHandler(ARINC485Request, self.handler)

    ## Handles incoming messages
    #  Receives tzmq request and passes it to the QTA running on the IFE VM
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  ARINC485Response object
    def handler(self, msg):
        response = ARINC485Response()
        ifeVmQtaResponse = self.ifeVmQtaClient.sendRequest(msg)

        if ifeVmQtaResponse.name == "ARINC485Response":
            deserializedResponse = ARINC485Response()
            deserializedResponse.ParseFromString(ifeVmQtaResponse.serializedBody)
            ifeVmQtaResponse.body = deserializedResponse
            return ifeVmQtaResponse
        else:
            self.log.error("Unexpected response from IFE VM ARINC485: %s" % ifeVmQtaResponse.name)
            response.state = ARINC485Response.STOPPED

        return ThalesZMQMessage(response)