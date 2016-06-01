
import os
import time
from common.tzmq.ThalesZMQServer import ThalesZMQServer
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.ARINC717Driver_pb2 import Request, Response


## ARINC 717 Driver Simulator class
#
# Implements a subset of the ARINC 717 Driver service, as specified
# in the "MPS ARINC 717 Driver ICD".
# Specifically, it implements the Request message on the Request/Response
# connection, with the following limitations:
#   - Only request of type RECEIVE_FRAME are supported; other request types
#     will return NOT_SUPPORTED
#   - Frame timestamp is just current time expressed in milliseconds
#   - Frame data is static and always of the same length
#   - Frame out_of_sync will be asserted every other frame request
#
# The ARINC 717 Driver ZMQ service uses IPC at ipc:///tmp/arinc/driver/717/device
# per the "MAP Network Configuration" document.
#
class ARINC717DriverSimulator(ThalesZMQServer):
    def __init__(self):
        # Make the directory for the IPC link, otherwise ZMQ won't init
        ipcdir = "/tmp/arinc/driver/717"
        if not os.path.exists(ipcdir):
            os.makedirs(ipcdir)

        # Now we can init the base class
        super(ARINC717DriverSimulator, self).__init__("ipc:///tmp/arinc/driver/717/device")

        # Keep an "out of sync" flag so we can return different values
        self.outOfSync = False

        print "Started ARINC 717 Driver simulator on", self.address

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleRequest(self, request):
        if request.name == "Request":
            # Parse request message
            requestMsg = Request()
            requestMsg.ParseFromString(request.serializedBody)

            # Create a ARINC 717 Response message for the results
            responseMsg = Response()

            if requestMsg.type == Request.RECEIVE_FRAME:
                # Receive Frame request - we support this
                responseMsg.type = Response.FRAME
                responseMsg.errorCode = Response.NONE
                responseMsg.frame.timestamp = int(time.time() * 1000)

                # TODO: generate better data
                responseMsg.frame.data = b"11abcdef12abcdef13abcdef14abcdef" \
                                         b"21abcdef22abcdef23abcdef24abcdef" \
                                         b"31abcdef32abcdef33abcdef34abcdef" \
                                         b"41abcdef42abcdef43abcdef44abcdef"

                # Toggle outOfSync flag each request
                responseMsg.frame.out_of_sync = self.outOfSync
                self.outOfSync = not self.outOfSync

            elif requestMsg.type == Request.GET_CONFIG:
                # Get Config request - unsupported
                responseMsg.type = Response.CONFIG
                responseMsg.errorCode = Response.NOT_SUPPORTED

            elif requestMsg.type == Request.SET_CONFIG:
                # Set Config request - unsupported
                responseMsg.type = Response.STATUS
                responseMsg.errorCode = Response.NOT_SUPPORTED

            else:
                # Unknown request type
                responseMsg.type = Response.FRAME # Field is required, have to put something there
                responseMsg.errorCode = Response.INVALID_REQ

            # Send response back to client
            self.sendResponse(ThalesZMQMessage(responseMsg))

        else:
            print "Error! Unknown request type"
            # Send "Unsupported Message" error back to client
            self.sendUnsupportedMessageErrorResponse()


if __name__ == "__main__":
    simulator = ARINC717DriverSimulator()
    simulator.run()
    print "Exit ARINC 717 Driver simulator"
