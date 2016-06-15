
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.GPIOManager_pb2 import RequestMessage, ResponseMessage

# @cond doxygen_unittest

## GPIO Manager Simulator Tester class
#
class GPIOManagerClient(ThalesZMQClient):
    ## Constructor
    #
    def __init__(self):
        super(GPIOManagerClient, self).__init__("ipc:///tmp/gpio-mgr.sock")

    ## Sends a Get Request message to the simulator and prints the response
    #
    def sendGetRequest(self, pin):
        # Create a request of type GET
        getReq = RequestMessage()
        getReq.pin_name = pin
        getReq.request_type = RequestMessage.GET
        print "\nRequest:  Get", pin

        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(getReq))

        # Parse the response
        if response.name == "ResponseMessage":
            getResp = ResponseMessage()
            getResp.ParseFromString(response.serializedBody)
            if getResp.error == ResponseMessage.OK:
                print "Response: Get", getResp.pin_name, ":", getResp.state
            else:
                print "Response: Failed to get", getResp.pin_name
        elif response.name == "ErrorMessage":
            print "Got error message from server"
        else:
            print "Error! Unknown response type"

    ## Sends a Set Request message to the simulator and prints the response
    #
    def sendSetRequest(self, pin, value):
        # Create a simple (one property) SetReq
        setReq = RequestMessage()
        setReq.pin_name = pin
        setReq.request_type = RequestMessage.SET
        setReq.value = value
        print "\nRequest:  Set", pin, ":", value

        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(setReq))

        # Parse the response
        if response.name == "ResponseMessage":
            setResp = ResponseMessage()
            setResp.ParseFromString(response.serializedBody)
            if setResp.error == ResponseMessage.OK:
                print "Response: Set", setResp.pin_name, ":", setResp.state
            else:
                print "Response: Failed to set", setResp.pin_name
        elif response.name == "ErrorMessage":
            print "Got error message from server"
        else:
            print "Error! Unknown response type"


if __name__ == "__main__":
    # Create a GPIOManagerClient instance; this will open a connection to the simulator
    client = GPIOManagerClient()

    # Send some get/set requests.
    client.sendGetRequest("OUTPUT_5_PIN_E6")
    client.sendGetRequest("INPUT_5_PIN_E7")
    client.sendSetRequest("OUTPUT_5_PIN_E6", True)
    client.sendGetRequest("OUTPUT_5_PIN_E6")
    client.sendGetRequest("INPUT_5_PIN_E7")
    client.sendSetRequest("OUTPUT_5_PIN_E6", False)
    client.sendGetRequest("OUTPUT_5_PIN_E6")
    client.sendGetRequest("INPUT_5_PIN_E7")
    client.sendGetRequest("BOGUS_PIN")
    client.sendSetRequest("BOGUS_PIN", True)
## @endcond
