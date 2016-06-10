
import zmq
from common.gpb.python.ErrorMessage_pb2 import ErrorMessage
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage


## Thales ZMQ Server class
#
# Binds to a ZMQ socket and accepts messages that uses the ZMQ-GPB protocol
# as defined by the "Thales Common Network Messaging" document and allows
# receiving requests and sending responses (REQ-REP ZMQ pattern).
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

            response = None

            # We expect Thales messages to have 3 parts
            if len(requestData) >= 3:
                # If message has more than 3 parts, log a warning, but proceed anyway
                if len(requestData) > 3:
                    print "Warning: received request message with", len(requestData), "parts"

                # Package request data into a message object
                request = ThalesZMQMessage(name=str(requestData[0]))
                request.header.ParseFromString(requestData[1])
                request.serializedBody = requestData[2]

                # Hand the request off to to HandleRequest(), which will return the response
                response = self.handleRequest(request)
            else:
                print "Malformed message received; ignoring"
                response = self.getMalformedMessageErrorResponse()

            # Send the response message back to the client.
            # Thales message is a multipart message made up of string name,
            # serialized header, and serialized body
            self.zsocket.send_multipart((response.name, response.serializedHeader, response.serializedBody))

    ## Called when a request is received from a client.
    #
    # Should be implemented in the derived class, and must return a
    # response message or error message to send back to the client.
    #
    # @param request ThalesZMQMessage containing received request
    # @return        ThalesZMQMessage response to send back to the client
    def handleRequest(self, request):
        # Base class method just returns an "Unsupported message" error response.
        # Derived class should override this and do something useful.
        return self.getUnsupportedMessageErrorResponse()

    ## Returns an error response message
    #
    # @param code Numeric error code
    # @param description Text description of error
    # @return ThalesZMQMessage containing ErrorMessage
    @staticmethod
    def getErrorResponse(code, description):
        # Create an ErrorMessage and encapsulate in a ThalesZMQMessage
        errorMessage = ErrorMessage()
        errorMessage.error_code = code
        errorMessage.error_description = description
        return ThalesZMQMessage(errorMessage)

    ## Returns an error response message of type "Unsupported message"
    #
    # @return ThalesZMQMessage containing ErrorMessage
    @staticmethod
    def getUnsupportedMessageErrorResponse():
        # Note: This error code was taken from the HDDS ICD; may not be correct usage
        return ThalesZMQServer.getErrorResponse(1000, "Unsupported message received")

    ## Returns an error response message of type "Malformed message"
    #
    # @return ThalesZMQMessage containing ErrorMessage
    @staticmethod
    def getMalformedMessageErrorResponse():
        # Note: This error code was taken from the HDDS ICD; may not be correct usage
        return ThalesZMQServer.getErrorResponse(1000, "Malformed message received")
