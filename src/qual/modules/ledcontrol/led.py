from qual.pb2.LED_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.pb2.GPIOManager_pb2 import *



## LED Control Module class
#
class Led(Module):
    ## Constructor
    def __init__(self, config=None):
        # Init the parent class
        super(Led, self).__init__(None)
        # Init the ThalesZMQClient
        self.gpioMgrClient = ThalesZMQClient(address="ipc:///tmp/gpio-mgr.sock", log=self.log, msgParts=1)
        # adding the message handler
        self.addMsgHandler(LEDRequest, self.handlerMessage)

    ## Called by base class when a request is received from a client.
    #
    #  @param request ThalesZMQMessage object containing received request
    def handlerMessage(self, thalesZMQMessage):
        # Get the the values according to the message
        (strState, boolState, strLed) = self.__stateLed(thalesZMQMessage.body.state, thalesZMQMessage.body.led)
        # Log the message request
        self.log.debug('Message received: (%s,%s)' %  (strState, strLed) )
        # Send the message to the GPIO simulator/driver
        msg = RequestMessage()
        msg.pin_name = strLed
        msg.request_type = RequestMessage.SET
        msg.value = boolState
        response =  self.gpioMgrClient.sendRequest(ThalesZMQMessage(msg))
        # Deserialize the response
        getResp = ResponseMessage()
        getResp.ParseFromString(response.serializedBody)
        # success???
        ledResponse = LEDResponse()
        if getResp.error == ResponseMessage.OK:
            ledResponse.success = True
        else:
            ledResponse.errorMessage = 'GPIO Error code: %' % (getResp.error)
            ledResponse.success = False

        return ThalesZMQMessage(ledResponse)

    ## Returns the state and the led name
    #  @param: state
    #  @param: led
    #  @return: (str State, str LED)
    def __stateLed(self, state, led):
        (strState, boolState,strLed) = ('UNKNOWN', False, 'UNKNOWN')
        if state == LS_ON:
            strState = 'ON'
            boolState = True
        if state == LS_OFF:
            strState = 'OFF'
            boolState = False
        if led == LED_POST:
            strLed = 'Post_LED'
        if led == LED_STATUS_GREEN:
            strLed = 'Status_LED_Green'
        if led == LED_STATUS_YELLOW:
            strLed = 'Status_LED_Yellow'

        return (strState, boolState,strLed)

