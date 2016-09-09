from common.pb2.GPIOManager_pb2 import RequestMessage, ResponseMessage, INPUT, OUTPUT
from tklabs_utils.logger import logger
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.tzmq.ThalesZMQServer import ThalesZMQServer


## GPIO Manager Simulator class
#
# Implements a subset of the GPIO Manager service, as specified
# in the "MPS GPIO Manager ICD".  Specifically, it implements the
# RequestMessage and ResponseMessage messages, with the following limitations:
#   - The list of supported pins is very small (but easily added to)
#   - No error checking for setting input pins
#   - "direction" field in response may not be accurate
#
# The GPIO Manager ZMQ service uses IPC at ipc:///tmp/gpio-mgr.sock
# per the "MAP Network Configuration" document.
#
# In addition, GPIO loopback is simulated by having a static table that
# defines output to input connections, and whenever an output pin in that
# table is changed by a SET request, the linked input pin's value is changed.
#
class GPIOManagerSimulator(ThalesZMQServer):
    ## Constructor
    #
    def __init__(self):
        # TODO: On target system this needs to be on VLAN 301, IP address 192.168.1.4
        # per the "MAP Network Configuration" document.
        super(GPIOManagerSimulator, self).__init__(address="ipc:///tmp/gpio-mgr.sock",
                                                   msgParts=1)

        # Turn down ThalesZMQServer debug level
        self.log.setLevel(logger.INFO)

        # List of pins that can be get/set
        self.pins = {"OUTPUT_1_PIN_A6"   :False,
                     "OUTPUT_2_PIN_B6"   :False,
                     "OUTPUT_3_PIN_C6"   :False,
                     "OUTPUT_4_PIN_D6"   :False,
                     "OUTPUT_5_PIN_E6"   :False,
                     "OUTPUT_6_PIN_E8"   :False,
                     "INPUT_1_PIN_A7"    :False,
                     "INPUT_2_PIN_B7"    :False,
                     "INPUT_3_PIN_C7"    :False,
                     "INPUT_4_PIN_D7"    :False,
                     "INPUT_5_PIN_E7"    :False,
                     "PA_All_PIN_C8"     :False,
                     "RxLineSelect_717"  :False,
                     "LED_POST"          :False,
                     "LED_STATUS_GREEN"  :False,
                     "LED_STATUS_YELLOW" :False}

        # Simulate GPIO loopback by linking outputs to inputs
        self.loopbackMap = {"OUTPUT_1_PIN_A6": "INPUT_1_PIN_A7",
                            "OUTPUT_2_PIN_B6": "INPUT_2_PIN_B7",
                            "OUTPUT_3_PIN_C6": "INPUT_3_PIN_C7",
                            "OUTPUT_4_PIN_D6": "INPUT_4_PIN_D7",
                            "OUTPUT_5_PIN_E6": "INPUT_5_PIN_E7",
                            "OUTPUT_6_PIN_E8": "PA_All_PIN_C8"}

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleRequest(self, request):
        # Route messages based on type
        if request.name == self.defaultRequestName:
            return self.handleGpioReq(request)
        else:
            print "Error! Unsupported request type"
            return self.getUnsupportedMessageErrorResponse()

    ## Handle GPIO requests
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleGpioReq(self, request):
        # Parse request
        gpioReq = RequestMessage()
        gpioReq.ParseFromString(request.serializedBody)

        # Create a ResponseMessage message for the results
        gpioResp = ResponseMessage()
        gpioResp.pin_name = gpioReq.pin_name

        if gpioReq.pin_name not in self.pins:
            print "Request with unknown pin_name:", gpioReq.pin_name
            gpioResp.state = False
            gpioResp.direction = OUTPUT
            gpioResp.error = ResponseMessage.IMPROPER_PIN_NAME

        elif gpioReq.request_type == RequestMessage.GET:
            # print "Get request:", gpioReq.pin_name
            gpioResp.state = self.pins[gpioReq.pin_name]
            gpioResp.direction = INPUT
            gpioResp.error = ResponseMessage.OK

        elif gpioReq.request_type == RequestMessage.SET:
            # print "Set request:", gpioReq.pin_name, ":", gpioReq.value
            self.pins[gpioReq.pin_name] = gpioReq.value
            gpioResp.state = gpioReq.value
            gpioResp.direction = OUTPUT
            gpioResp.error = ResponseMessage.OK
            # If this is a GPIO output, simulate loopback by setting linked input value
            if gpioReq.pin_name in self.loopbackMap:
                #print "Setting linked GPIO", self.loopbackMap[gpioReq.pin_name], ":", gpioReq.value
                self.pins[self.loopbackMap[gpioReq.pin_name]] = gpioReq.value

        else:
            print "Request with unknown request_type:", gpioReq.request_type
            gpioResp.state = False
            gpioResp.direction = OUTPUT
            gpioResp.error = ResponseMessage.IMPROPER_REQUEST_TYPE

        # Send response back to client
        return ThalesZMQMessage(gpioResp)


if __name__ == "__main__":
    simulator = GPIOManagerSimulator()
    simulator.run()
    print "Exit GPIOManager simulator"
