
import zmq
from common.gpb.python.ErrorMessage_pb2 import ErrorMessage
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage


class ThalesZMQServer(object):
    """
    Binds to a ZMQ socket and accepts messages that uses the ZMQ-GPB protocol
    as defined by the "Thales Common Network Messaging" document and allows
    receiving requests and sending responses.
    """

    def __init__(self, address):
        """
        Constructor

        @param address ZMQ address string for socket to bind to
        """

        self.zcontext = zmq.Context.instance()
        self.zsocket = self.zcontext.socket(zmq.REP)
        self.zsocket.bind(address)

    def Run(self):
        """
        Starts up a loop that handles requests.  Will not return.
        """

        while True:
            # This will block waiting for a request
            requestData = self.zsocket.recv_multipart()

            # We expect Thales messages to have 3 parts
            if len(requestData) >= 3:
                # If message has more than 3 parts, log a warning, but proceed anyway
                if len(requestData) > 3:
                    print "Warning: received request message with", len(requestData), "parts"

                # Package request data into a message object and hand off to HandleRequest()
                request = ThalesZMQMessage(str(requestData[0]))
                request.header.ParseFromString(requestData[1])
                request.serializedBody = requestData[2]
                self.HandleRequest(request)
            else:
                print "Malformed message received; ignoring"
                self.SendErrorResponse(1, "Malformed Message")

    def HandleRequest(self, request):
        """
        Method called when a request is received from a client.
        Should be implemented in the derived class, and should call a method that sends a
        response message or error message back to the client.

        @param request ThalesZMQMessage object containing received request
        """

        # Base class method just sends an "Unexpected Message" error response.
        # Derived class should override this and do something useful.
        self.SendUnexpectedMessageErrorResponse()

    def SendResponse(self, response):
        """
        Sends a (non-error) response to the client

        @param response ThalesZMQMessage object containing response to send
        """

        # Thales message is a multipart message made up of string name,
        # serialized header, and serialized body
        self.zsocket.send_multipart((response.name, response.serializedHeader, response.serializedBody))

    def SendErrorResponse(self, code, description):
        """
        Sends an error response to the client

        @param code Numeric error code
        @param description Text description of error
        """

        # Create an ErrorMessage and encapsulate in a ThalesZMQMessage
        errorMessage = ErrorMessage()
        errorMessage.error_code = code
        errorMessage.error_description = description
        response = ThalesZMQMessage("ErrorMessage", errorMessage)

        # Send the message as the response
        self.SendResponse(response)

    def SendUnexpectedMessageErrorResponse(self):
        """
        Sends an error response of type "Unexpected message" to the client
        """
        self.SendErrorResponse(2, "Unexpected Message")
