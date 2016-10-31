from time import sleep

from common.pb2.ARINC717Driver_pb2 import Request, Response
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


# @cond doxygen_unittest

## ARINC 717 Driver Simulator Tester class
#
class ARINC717DriverClient(ThalesZMQClient):
    ## Constructor
    #
    def __init__(self):
        super(ARINC717DriverClient, self).__init__(address="ipc:///tmp/arinc/driver/717/device",
                                                   msgParts=1)

    ## Sends a "Request" message to the simulator and prints the response
    #
    def sendReqMsg(self):
        # Create a ARINC717 request message
        requestMsg = Request()
        requestMsg.type = Request.RECEIVE_FRAME

        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(requestMsg))

        # Parse the response
        if response.name == self.defaultResponseName:
            responseMsg = Response()
            responseMsg.ParseFromString(response.serializedBody)
            print responseMsg
        elif response.name == "ErrorMessage":
            print "Got error message from server"
        else:
            print "Error! Unknown response type"


if __name__ == "__main__":
    # Create a ARINC717DriverClient instance; this will open a connection to the simulator
    client = ARINC717DriverClient()

    # Send some requests.
    print "\nResponse from first request:"
    client.sendReqMsg()

    sleep(0.5)
    print "\nResponse from second request:"
    client.sendReqMsg()
## @endcond
