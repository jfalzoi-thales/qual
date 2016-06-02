
import zmq
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage


## Thales ZMQ Client class
#
# Establishes a ZMQ connection to a server that uses the ZMQ-GPB protocol
# as defined by the "Thales Common Network Messaging" document and allows
# sending requests and receiving responses.
#
# Can be subclassed, or can just be used directly like this:
#   client = ThalesZMQClient("tcp://localhost:5555")
#   response = client.sendRequest(request)
#@ingroup zmq
class ThalesZMQClient(object):
    ## Constructor
    #
    # @param address ZMQ address string of server to connect to
    def __init__(self, address):
        self.zcontext = zmq.Context.instance()
        self.zsocket = self.zcontext.socket(zmq.REQ)
        self.zsocket.connect(address)

    ## Sends a request to the connected server and waits for the server's response
    #
    # @param request ThalesZMQMessage object containing request to send
    # @return ThalesZMQMessage object containing received response
    #
    def sendRequest(self, request):
        # Thales ZMQ message is a multipart message made up of string name,
        # serialized header, and serialized body
        self.zsocket.send_multipart((request.name, request.serializedHeader, request.serializedBody))

        # This will block waiting for the response
        responseData = self.zsocket.recv_multipart()

        # We expect Thales messages to have 3 parts
        if len(responseData) >= 3:
            # If message has more than 3 parts, log a warning, but proceed anyway
            if len(responseData) > 3:
                print "Warning: received response message with", len(responseData), "parts"

            # Package response data into a message object
            response = ThalesZMQMessage(name=str(responseData[0]))
            response.header.ParseFromString(responseData[1])
            response.serializedBody = responseData[2]
            return response
        else:
            print "Malformed message received"
            # Create an empty message object to return
            response = ThalesZMQMessage()
            return response
