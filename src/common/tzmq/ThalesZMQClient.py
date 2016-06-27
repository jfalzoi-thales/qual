
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
    # @param address ZMQ address string of server to connect to
    # @param timeout How long to wait for responses from the server
    # @param log     Logger to use to log communication errors
    def __init__(self, address, timeout=200, log=None):
        ## Address to connect to
        self.address = address
        ## How long to wait for responses
        self.timeout = timeout
        ## Logger
        self.log = log

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
        # Thales ZMQ message is a multipart message made up of string name,
        # serialized header, and serialized body
        self.zsocket.send_multipart((request.name, request.serializedHeader, request.serializedBody))

        # Try to receive the response
        try:
            responseData = self.zsocket.recv_multipart()
        except zmq.error.Again:
            responseData = None
            # Close and reopen the socket
            self.closeSocket()
            self.openSocket()

        # We expect Thales messages to have 3 parts
        if responseData is not None and len(responseData) >= 3:
            # If message has more than 3 parts, log a warning, but proceed anyway
            if len(responseData) > 3:
                self.log.warning("Received response message with %d parts" % len(responseData))

            # Package response data into a message object
            response = ThalesZMQMessage(name=str(responseData[0]))
            response.header.ParseFromString(responseData[1])
            response.serializedBody = responseData[2]
            return response

        if responseData is None:
            self.log.error("Timeout waiting for response from %s" % self.address)
        else:
            self.log.warning("Malformed message received")
        # Return an empty response object
        return ThalesZMQMessage()
