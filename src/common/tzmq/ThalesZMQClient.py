
import zmq
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger


## Thales ZMQ Client class
#
# Establishes a ZMQ connection to a server that uses the ZMQ-GPB protocol
# as defined by the "Thales Common Network Messaging" document and allows
# sending requests and receiving responses.
#
# Can be subclassed, or can just be used directly like this:
#   client = ThalesZMQClient("tcp://localhost:5555")
#   response = client.sendRequest(request)
class ThalesZMQClient(object):
    ## Constructor
    #
    # @param address       ZMQ address string of server to connect to
    # @param timeout       How long to wait for responses from the server
    # @param log           Logger to use to log communication errors
    # @param msgParts      Number of message parts for both request and response
    # @param requestParts  Number of message parts for request
    # @param responseParts Number of message parts for response
    def __init__(self, address, timeout=500, log=None, msgParts=3, requestParts=0, responseParts=0):
        ## Address to connect to
        self.address = address
        ## Number of message parts to use for request
        self.requestParts = requestParts if requestParts > 0 else msgParts
        ## Number of message parts to use for response
        self.responseParts = responseParts if responseParts > 0 else msgParts
        ## How long to wait for responses
        self.timeout = timeout
        ## Logger
        self.log = log
        ## Default response name, used for single-part messages
        self.defaultResponseName = "Response"

        # If no logger was provided, go ahead and create one
        if self.log is None:
            self.log = Logger()

        ## ZMQ context
        self.zcontext = zmq.Context.instance()
        ## ZMQ socket
        self.zsocket = None
        self.openSocket()

    ## Opens the ZMQ socket
    def openSocket(self):
        self.log.debug("Opening socket connection to %s" % self.address)
        self.zsocket = self.zcontext.socket(zmq.REQ)
        self.zsocket.set(zmq.RCVTIMEO, self.timeout)
        self.zsocket.connect(self.address)

    ## Closes the ZMQ socket
    def closeSocket(self):
        self.log.debug("Closing socket connection to %s" % self.address)
        self.zsocket.close(linger=1)
        self.zsocket = None

    ## Sends a request to the connected server and waits for the server's response
    #
    # @param request ThalesZMQMessage object containing request to send
    # @return ThalesZMQMessage object containing received response
    #
    def sendRequest(self, request):
        if self.requestParts == 3:
            # "Thales Common Network Messaging" format has 3 parts: name, header, body
            self.zsocket.send_multipart((request.name, request.serializedHeader, request.serializedBody))
        elif self.requestParts == 2:
            # Two-part messages have a name and a body
            self.zsocket.send_multipart((request.name, request.serializedBody))
        else:
            # Single-part messages have just a body
            self.zsocket.send(request.serializedBody)

        # Try to receive the response
        try:
            responseData = self.zsocket.recv_multipart()
        except zmq.error.Again:
            responseData = None
            # Close and reopen the socket
            self.closeSocket()
            self.openSocket()

        # Check the message has the expected number of parts
        if responseData is not None and len(responseData) == self.responseParts:
            # Package response into a message object, handling the different message formats
            if self.responseParts == 3:
                # "Thales Common Network Messaging" format has 3 parts: name, header, body
                response = ThalesZMQMessage(name=str(responseData[0]))
                response.header.ParseFromString(responseData[1])
                response.serializedBody = responseData[2]
            elif self.responseParts == 2:
                # Two-part messages have a name and a body
                response = ThalesZMQMessage(name=str(responseData[0]))
                response.serializedBody = responseData[1]
            else:
                # Single-part messages have just a body; give message object a default name
                response = ThalesZMQMessage(name=self.defaultResponseName)
                response.serializedBody = responseData[0]
            return response

        if responseData is None:
            self.log.error("Timeout waiting for response from %s" % self.address)
        else:
            self.log.error("Malformed message received (%d parts, expected %d)" % (len(requestData), self.responseParts))

        # Return an empty response object
        return ThalesZMQMessage()
