import os
import subprocess

from common.pb2.GPIOManager_pb2 import RequestMessage, ResponseMessage, INPUT, OUTPUT, UNKNOWN_DIR
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage

## Discard the output
DEVNULL = open(os.devnull, 'wb')

## IFEGPIO Class
class IFEGPIO(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        super(IFEGPIO, self).__init__(config)
        ## List of supported input pins
        self.inputPins = ["LLS_IN_GP_KL_01", "LLS_IN_GP_KL_02", "LLS_IN_GP_KL_03", "LLS_IN_GP_KL_04",
                          "PA_KLIN1", "PA_KLIN2", "PA_KLIN3", "PA_KLIN4", "PA_KLIN5", "PA_KLIN6", "PA_KLIN7",
                          "PA_KLIN8", "PA_MUTE"]
        ## List of supported output pins
        self.outputPins = ["LLS_OUT_GP_KL_01", "LLS_OUT_GP_KL_02", "LLS_OUT_GP_KL_03",
                           "VA_KLOUT1", "VA_KLOUT2", "VA_KLOUT3", "VA_KLOUT4", "VA_KLOUT5", "VA_KLOUT6"]
        ## Lock to prevent running fpga command line tools at the same time as Analog Audio module
        self.commandLock = self.getNamedLock("commandLock")
        #  Add IFEGPIO Message handler
        self.addMsgHandler(RequestMessage, self.handleRequest)

    ## Called by base class when a request is received from a client.
    #  @param   msg ThalesZMQMessage object containing received request
    #  @return  ThalesZMQMessage object containing a response
    def handleRequest(self, msg):
        #  Route messages based on type
        if msg.name == "RequestMessage":
            response = ResponseMessage()
            response.pin_name = msg.body.pin_name

            if msg.body.request_type == RequestMessage.GET:
                self.handleGet(msg.body, response)
            elif msg.body.request_type == RequestMessage.SET:
                self.handleSet(msg.body, response)
            else:
                self.log.error("Unexpected Request Type %d" % msg.body.request_type)
                response.direction = UNKNOWN_DIR
                response.state = False
                response.error = ResponseMessage.IMPROPER_REQUEST_TYPE

            return ThalesZMQMessage(response)
        else:
            self.log.error("Error! Unsupported request type: %s" % msg.name)

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
            #  Assume DRIVER_ERR unless we set it otherwise
            response.error = ResponseMessage.GPIO_DRIVER_ERR

            if request.pin_name.startswith("LLS"):
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
            else:
                reg = '0xF1' if request.pin_name == "PA_MUTE" else '0xF0'
                cmd = 'fpga %s' % reg
                self.log.debug(cmd)
                try:
                    self.commandLock.acquire()
                    output = subprocess.check_output(cmd, shell=True)
                    self.commandLock.release()
                except subprocess.CalledProcessError:
                    self.log.error("Error return from fpga for pin %s" % request.pin_name)
                else:
                    if output != "":
                        pin = int(request.pin_name.split("PA_KLIN")[1]) - 1 if request.pin_name != 'PA_MUTE' else 2

                        if int(output, 16) & (1 << pin):
                            response.state = True
                            response.error = ResponseMessage.OK
                        else:
                            response.state = False
                            response.error = ResponseMessage.OK

                    if response.error != ResponseMessage.OK:
                        self.log.error("Unexpected output from fpga for pin %s" % request.pin_name)

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
            #  Assume DRIVER_ERR unless we set it otherwise
            response.error = ResponseMessage.GPIO_DRIVER_ERR

            if request.pin_name.startswith("LLS"):
                cmd = 'demo_binaryio setDiscreteOutput %s %d' % (request.pin_name, 1 if request.value else 0)
                self.log.debug(cmd)
                rc = subprocess.call(cmd, shell=True, stdout=DEVNULL)

                if rc != 0:
                    self.log.error("Error return from demo_binaryio for pin %s" % request.pin_name)
                else:
                    response.error = ResponseMessage.OK
            else:
                cmd = 'fpga 0x8B'
                self.log.debug(cmd)
                try:
                    self.commandLock.acquire()
                    output = subprocess.check_output(cmd, shell=True)
                    self.commandLock.release()
                except subprocess.CalledProcessError:
                    self.log.error("Error return from fpga for pin %s" % request.pin_name)
                else:
                    if output != "":
                        pin = int(request.pin_name.split("VA_KLOUT")[1]) - 1

                        if request.value:
                            write = hex(int(output, 16) | (1 << pin))
                        else:
                            write = hex(int(output, 16) & ~(1 << pin))

                        cmd = 'fpga 0x8B %s' % str(write)
                        self.commandLock.acquire()
                        rc = subprocess.call(cmd, shell=True, stdout=DEVNULL)
                        self.commandLock.release()

                        if rc != 0:
                            self.log.error("Error return from fpga for pin %s" % request.pin_name)
                        else:
                            response.error = ResponseMessage.OK
