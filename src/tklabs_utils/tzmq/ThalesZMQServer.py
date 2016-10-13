import zmq
from tklabs_utils.logger.logger import Logger
from tklabs_utils.pb2.ErrorMessage_pb2 import ErrorMessage
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


## Thales ZMQ Server class
#
# Binds to a ZMQ socket and accepts messages that uses the ZMQ-GPB protocol
# as defined by the "Thales Common Network Messaging" document and allows
# receiving requests and sending responses (REQ-REP ZMQ pattern).
class ThalesZMQServer(object):
    ## Constructor
    #
    # @param address       ZMQ address string for socket to bind to
    # @param msgParts      Number of message parts for both request and response
    # @param requestParts  Number of message parts for request
    # @param responseParts Number of message parts for response
    def __init__(self, address, msgParts=3, requestParts=0, responseParts=0, allowNoBody=False):
        ## Logger implementation, based on standard python logger
        self.log = Logger(type(self).__name__)
        ## ZMQ address for socket to bind to
        self.address = address
        ## Number of message parts to use for request
        self.requestParts = requestParts if requestParts > 0 else msgParts
        ## Number of message parts to use for response
        self.responseParts = responseParts if responseParts > 0 else msgParts
        ## Whether to allow messages with no body
        self.allowNoBody = allowNoBody
        ## Default request name, used for single-part messages
        self.defaultRequestName = "Request"
        ## ZMQ context
        self.zcontext = zmq.Context.instance()
        ## ZMQ socket
        self.zsocket = self.zcontext.socket(zmq.REP)
        self.zsocket.bind(self.address)

    ## Starts up a loop that handles requests.
    #
    # Will only return if canceled (e.g. Ctrl-C).
    #
    def run(self):
        self.log.info("Listening for GPB requests on %s" % self.address)
        while True:
            # This will block waiting for a request
            try:
                requestData = self.zsocket.recv_multipart()
            except KeyboardInterrupt:
                return

            response = None

            # Check the message has the expected number of parts
            if len(requestData) == self.requestParts or (self.allowNoBody and len(requestData) == 2 and self.requestParts == 3):
                # Package request data into a message object, handling the different message formats
                if self.requestParts == 3:
                    # "Thales Common Network Messaging" format has 3 parts: name, header, body
                    request = ThalesZMQMessage(name=str(requestData[0]))
                    request.header.ParseFromString(requestData[1])
                    if len(requestData) == 3:
                        request.serializedBody = requestData[2]
                    else:
                        self.log.info("Message had no body, allowed since allowNoBody=True")
                elif self.requestParts == 2:
                    # Two-part messages have a name and a body
                    request = ThalesZMQMessage(name=str(requestData[0]))
                    request.serializedBody = requestData[1]
                else:
                    # Single-part messages have just a body; give message object a default name
                    request = ThalesZMQMessage(name=self.defaultRequestName)
                    request.serializedBody = requestData[0]
                self.log.debug("Received GPB %s (%d parts)" % (request.name, len(requestData)))

                # Hand the request off to to HandleRequest(), which will return the response
                response = self.handleRequest(request)
            else:
                self.log.error("Malformed message received (%d parts, expected %d)" % (len(requestData), self.requestParts))
                response = self.getMalformedMessageErrorResponse()

            # Send the response message back to the client.
            self.log.debug("Sending GPB %s (%d parts)" % (response.name, self.responseParts))
            if self.responseParts == 3:
                # "Thales Common Network Messaging" format has 3 parts: name, header, body
                self.zsocket.send_multipart((response.name, response.serializedHeader, response.serializedBody))
            elif self.responseParts == 2:
                # Two-part messages have a name and a body
                self.zsocket.send_multipart((response.name, response.serializedBody))
            else:
                # Single-part messages have just a body
                self.zsocket.send(response.serializedBody)

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
