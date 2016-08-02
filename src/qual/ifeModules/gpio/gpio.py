import subprocess
import os
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.GPIOManager_pb2 import RequestMessage, ResponseMessage, INPUT, OUTPUT, UNKNOWN_DIR
from common.module.module import Module


## Discard the output
DEVNULL = open(os.devnull, 'wb')


## GPIO Module for IFE sensors
class IFEGPIO(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        #  Initialize parent class
        super(IFEGPIO, self).__init__(config)
        ## List of supported input pins
        self.inputPins = ["LLS_IN_GP_KL_01", "LLS_IN_GP_KL_02", "LLS_IN_GP_KL_03", "LLS_IN_GP_KL_04"]
        ## List of supported output pins
        self.outputPins = ["LLS_OUT_GP_KL_01", "LLS_OUT_GP_KL_02", "LLS_OUT_GP_KL_03"]
        #  Add handler to available message handlers
        self.addMsgHandler(RequestMessage, self.handler)

    ## Handles incoming messages
    #  Receives tzmq request and runs requested process
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  ThalesZMQMessage object
    def handler(self, msg):
        request = msg.body
        response = ResponseMessage()
        response.pin_name = request.pin_name

        if request.request_type == RequestMessage.GET:
            self.handleGet(request, response)
        elif request.request_type == RequestMessage.SET:
            self.handleSet(request, response)
        else:
            self.log.error("Unexpected Request Type %d" % request.request_type)
            response.direction = UNKNOWN_DIR
            response.state = False
            response.error = ResponseMessage.IMPROPER_REQUEST_TYPE

        return ThalesZMQMessage(response)

    ## Handles incoming GET requests
    #  @param     self
    #  @param     request   GPIO RequestMessage object
    #  @param     response  GPIO ResponseMessage object
    def handleGet(self, request, response):
        response.direction = INPUT
        response.state = False

        if request.pin_name not in self.inputPins:
            self.log.error("Unknown GPIO input pin %s" % request.pin_name)
            response.error = ResponseMessage.IMPROPER_PIN_NAME
        else:
            # Assume DRIVER_ERR unless we set it otherwise
            response.error = ResponseMessage.GPIO_DRIVER_ERR
            cmd = 'demo_binaryio getDiscreteInput %s' % request.pin_name
            self.log.debug(cmd)
            try:
                output = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                self.log.error("Error return from demo_binaryio for pin %s" % request.pin_name)
            else:
                self.log.debug("Command returned: %s" % output)
                idx = output.find("Discrete value =")
                if idx > -1:
                    if output[idx + 17] == "0":
                        response.state = False
                        response.error = ResponseMessage.OK
                    elif output[idx + 17] == "1":
                        response.state = True
                        response.error = ResponseMessage.OK
                if response.error != ResponseMessage.OK:
                    self.log.error("Unexpected output from demo_binaryio for pin %s" % request.pin_name)


    ## Handles incoming SET requests
    #  @param     self
    #  @param     request   GPIO RequestMessage object
    #  @param     response  GPIO ResponseMessage object
    def handleSet(self, request, response):
        response.direction = OUTPUT
        response.state = request.value

        if request.pin_name not in self.outputPins:
            self.log.error("Unknown GPIO output pin %s" % request.pin_name)
            response.error = ResponseMessage.IMPROPER_PIN_NAME
        else:
            cmd = 'demo_binaryio setDiscreteOutput %s %d' % (request.pin_name, 1 if request.value else 0)
            self.log.debug(cmd)
            rc = subprocess.call(cmd, shell=True, stdout=DEVNULL)
            if rc != 0:
                self.log.error("Error return from demo_binaryio for pin %s" % request.pin_name)
                response.error = ResponseMessage.GPIO_DRIVER_ERR
            else:
                response.error = ResponseMessage.OK
