
import zmq
from common.gpb.python.ErrorMessage_pb2 import ErrorMessage
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage


## Thales ZMQ Server class
#
# Binds to a ZMQ socket and accepts messages that uses the ZMQ-GPB protocol
# as defined by the "Thales Common Network Messaging" document and allows
# receiving requests and sending responses (REQ-REP ZMQ pattern).
#
class ThalesZMQServer(object):
    ## Constructor
    #
    # @param address ZMQ address string for socket to bind to
    #
    def __init__(self, address):
        self.address = address
        self.zcontext = zmq.Context.instance()
        self.zsocket = self.zcontext.socket(zmq.REP)
        self.zsocket.bind(self.address)

    ## Starts up a loop that handles requests.
    #
    # Will only return if canceled (e.g. Ctrl-C).
    #
    def run(self):
        while True:
            # This will block waiting for a request
            try:
                requestData = self.zsocket.recv_multipart()
            except KeyboardInterrupt:
                return

            # We expect Thales messages to have 3 parts
            if len(requestData) >= 3:
                # If message has more than 3 parts, log a warning, but proceed anyway
                if len(requestData) > 3:
                    print "Warning: received request message with", len(requestData), "parts"

                # Package request data into a message object and hand off to HandleRequest()
                request = ThalesZMQMessage(name=str(requestData[0]))
                request.header.ParseFromString(requestData[1])
                request.serializedBody = requestData[2]
                self.handleRequest(request)
            else:
                print "Malformed message received; ignoring"
                self.sendMalformedMessageErrorResponse()

    ## Called when a request is received from a client.
    #
    # Should be implemented in the derived class, and should call a method that sends a
    # response message or error message back to the client.
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleRequest(self, request):
        # Base class method just sends an "Unsupported message" error response.
        # Derived class should override this and do something useful.
        self.sendUnsupportedMessageErrorResponse()

    ## Sends a (non-error) response to the client
    #
    # @param response ThalesZMQMessage object containing response to send
    #
    def sendResponse(self, response):
        # Thales message is a multipart message made up of string name,
        # serialized header, and serialized body
        self.zsocket.send_multipart((response.name, response.serializedHeader, response.serializedBody))

    ## Sends an error response to the client
    #
    # @param code Numeric error code
    # @param description Text description of error
    #
    def sendErrorResponse(self, code, description):
        # Create an ErrorMessage and encapsulate in a ThalesZMQMessage
        errorMessage = ErrorMessage()
        errorMessage.error_code = code
        errorMessage.error_description = description
        response = ThalesZMQMessage(errorMessage)

        # Send the message as the response
        self.sendResponse(response)

    ## Sends an error response of type "Unsupported message" to the client
    #
    def sendUnsupportedMessageErrorResponse(self):
        # Note: This error code was taken from the HDDS ICD; may not be correct usage
        self.sendErrorResponse(1000, "Unsupported GPB message received")

    ## Sends an error response of type "Malformed message" to the client
    #
    def sendMalformedMessageErrorResponse(self):
        # Note: This error code was taken from the HDDS ICD; may not be correct usage
        self.sendErrorResponse(1000, "Malformed GPB message received")
