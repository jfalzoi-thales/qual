from time import sleep
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.GPIOManager_pb2 import RequestMessage, ResponseMessage, INPUT, OUTPUT, UNKNOWN_DIR
from common.logger.logger import Logger

# @cond doxygen_unittest

## IFEGPIO tester class
class IFEGPIOClient(ThalesZMQClient):
    ## Constructor
    def __init__(self):
        super(IFEGPIOClient, self).__init__("tcp://localhost:50010")
        #  Set up a logger
        self.log = Logger(name='Test IFEGPIO')

    ## Send a request to the IFEGPIO, wait for the response, and write decoded response to log
    def sendReqAndLogResp(self, request):
        # Send request and get response
        response = self.sendRequest(request)
        body = ResponseMessage()
        body.ParseFromString(response.serializedBody)
        self.log.info("Received %s:\n%s" % (response.name, body))

    ## Series of tests for the CPULoading module
    #
    def test_IFEGPIO(self):
        message = RequestMessage()
        inputPins = ["LLS_IN_GP_KL_01", "LLS_IN_GP_KL_02", "LLS_IN_GP_KL_03", "LLS_IN_GP_KL_04"]
        outputPins = ["LLS_OUT_GP_KL_01", "LLS_OUT_GP_KL_02", "LLS_OUT_GP_KL_03"]

        self.log.info("Get All Inputs")

        for pin in inputPins:
            message.pin_name = pin
            message.request_type = RequestMessage.GET
            message.value = True
            self.sendReqAndLogResp(ThalesZMQMessage(message))
            sleep(3)

        self.log.info("Set All Outputs")

        for pin in outputPins:
            message.pin_name = pin
            message.request_type = RequestMessage.SET
            self.sendReqAndLogResp(ThalesZMQMessage(message))
            sleep(3)

if __name__ == "__main__":
    #  Create an IFEGPIOClient instance
    IFEGPIOClient().test_IFEGPIO()
## @endcond
