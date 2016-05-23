
import zmq
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage


class ThalesZMQClient(object):
    """
    Establishes a ZMQ connection to a server that uses the ZMQ-GPB protocol
    as defined by the "Thales Common Network Messaging" document and allows
    sending requests and receiving responses.
    """

    def __init__(self, address):
        """
        Constructor

        @param address ZMQ address string of server to connect to
        """

        self.zcontext = zmq.Context.instance()
        self.zsocket = self.zcontext.socket(zmq.REQ)
        self.zsocket.connect(address)

    def SendRequest(self, request):
        """
        Sends a request to the connected server and returns the server's response

        @param request ThalesZMQMessage object containing request to send
        @return ThalesZMQMessage object containing received response
        """

        # Thales ZMQ message is a multipart message made up of string name,
        # serialized header, and serialized body
        self.zsocket.send_multipart((request.name, request.serializedHeader, request.serializedBody))

        # Receive the response
        responseData = self.zsocket.recv_multipart()

        # Well-formed Thales messages must have 3 parts
        if len(responseData) >= 3:
            # Package response data into a message object
            response = ThalesZMQMessage(str(responseData[0]))
            response.header.ParseFromString(responseData[1])
            response.serializedBody = responseData[2]
            return response
        else:
            print "Malformed message received"
            # Create an empty message object to return
            response = ThalesZMQMessage("")
            return response
