
import sys
import os
import time
from common.logger import logger
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
    def __init__(self, wordRate=64):
        # Make the directory for the IPC link, otherwise ZMQ won't init
        ipcdir = "/tmp/arinc/driver/717"
        if not os.path.exists(ipcdir):
            os.makedirs(ipcdir)

        # Now we can init the base class
        super(ARINC717DriverSimulator, self).__init__("ipc:///tmp/arinc/driver/717/device")

        # Turn down ThalesZMQServer debug level
        self.log.setLevel(logger.INFO)

        # Keep an "out of sync" flag so we can return different values
        self.outOfSync = False

        # Save the word rate
        self.wordRate = wordRate

        self.log.info("Word rate is %d words/sec" % wordRate)

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

                # Generate frame data
                responseMsg.frame.data = self.genSubFrame(1) + \
                                         self.genSubFrame(2) + \
                                         self.genSubFrame(3) + \
                                         self.genSubFrame(4)

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
            return ThalesZMQMessage(responseMsg)

        else:
            print "Error! Unknown request type"
            # Send "Unsupported Message" error back to client
            return self.getUnsupportedMessageErrorResponse()

    def genSubFrame(self, subFrameNum):
        # Frame sync codes are defined by ARINC 717 standard
        # Yes, it defines them in octal.
        syncCodes = (0o1107, 0o2507, 0o5107, 0o6670)
        fakeData = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890#abcdefghijklmnopqrstuvwxyz"

        # Build a string, starting with the sync code.
        # ARINC 717 communicates in 12-bit words, and we put each word in two sequential bytes.
        bytes = bytearray(2 * self.wordRate)
        bytes[0] = syncCodes[subFrameNum - 1] >> 8
        bytes[1] = syncCodes[subFrameNum - 1] & 0xFF

        for i in range(1, self.wordRate):
            bytes[i * 2]     = subFrameNum      # Use the sub-frame number as top 4 bits
            bytes[i * 2 + 1] = fakeData[i % 64] # Printable characters for lower 8 bits

        # Return as a string
        return str(bytes)

if __name__ == "__main__":
    # Command-line argument can be used to specify number of words per sub-frame
    rate = 64
    if len(sys.argv) > 1:
        arg = int(sys.argv[1])
        # Make sure it's a valid rate
        if arg in (32, 64, 128, 256, 512, 1024, 2048, 4096, 8192):
            rate = arg
        else:
            print "Invalid rate specified; using default", rate

    simulator = ARINC717DriverSimulator(rate)
    simulator.run()
    print "Exit ARINC 717 Driver simulator"
