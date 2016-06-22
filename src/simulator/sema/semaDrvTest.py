
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.SEMA_pb2 import RequestStatusMessage, ResponseStatusMessage

# @cond doxygen_unittest

## SEMA Driver Simulator Tester class
#
class SEMADriverClient(ThalesZMQClient):
    ## Constructor
    #
    def __init__(self):
        super(SEMADriverClient, self).__init__("ipc:///tmp/sema-drv.sock")

    ## Sends a "RequestStatusMessage" message to the simulator and prints the response
    #
    def sendReqStatusMsg(self, name):
        # Create a SEMA request message
        requestMsg = RequestStatusMessage()
        requestMsg.name = name

        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(requestMsg))

        # Parse the response
        if response.name == "ResponseStatusMessage":
            responseMsg = ResponseStatusMessage()
            responseMsg.ParseFromString(response.serializedBody)
            if responseMsg.error == ResponseStatusMessage.STATUS_OK:
                print "Get", responseMsg.name, ":", responseMsg.value
            else:
                print "Failed to get", responseMsg.name
        elif response.name == "ErrorMessage":
            print "Got error message from server"
        else:
            print "Error! Unknown response type"


if __name__ == "__main__":
    # Create a SEMADriverClient instance; this will open a connection to the simulator
    client = SEMADriverClient()

    # Send some requests.
    client.sendReqStatusMsg("BIOSIndex")
    client.sendReqStatusMsg("BoardManufacturer")
    client.sendReqStatusMsg("BoardMaxTemp")
    client.sendReqStatusMsg("bogus_key")
## @endcond
