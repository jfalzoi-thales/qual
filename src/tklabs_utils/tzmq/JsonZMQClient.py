import json
import zmq

from tklabs_utils.logger.logger import Logger
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.tzmq.jsonConversion.jsonConversion import JsonConversion


## JSON ZMQ Client class
#
# Establishes a ZMQ connection to a server that uses the JSON-over-ZMQ
# protocol as defined by the "MPS Qualification Software ICD" and allows
# sending requests and receiving responses.
#
# Can be subclassed, or can just be used directly like this:
#   client = JsonZMQClient("tcp://localhost:5555")
#   response = client.sendRequest(request)
#
# Note that sendRequest accepts and returns ThalesZMQMessage objects;
# the conversion to and from JSON is done internally.
class JsonZMQClient(object):
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
        # Convert GPB response message to JSON
        try:
            reqName, reqJson = JsonConversion.gpb2json(request.body)
        except Exception as e:
            self.log.error("Failed to convert GPB to JSON: %s" % e.message)
            # Return an empty response object
            return ThalesZMQMessage()

        # JSON ZMQ message is a multipart message made up of string name and JSON body
        self.zsocket.send_multipart((reqName, json.dumps(reqJson)))

        # Try to receive the response
        try:
            responseData = self.zsocket.recv_multipart()
        except zmq.error.Again:
            responseData = None
            # Close and reopen the socket
            self.closeSocket()
            self.openSocket()

        # We expect JSON messages to have 2 parts
        if responseData is not None and len(responseData) >= 2:
            # If message has more than 2 parts, log a warning, but proceed anyway
            if len(responseData) > 2:
                self.log.warning("Received response message with %d parts" % len(responseData))

            # Response class name is in first part
            respName = str(responseData[0])

            # Convert JSON string to a GPB object
            try:
                respBody = JsonConversion.json2gpb(respName, json.loads(responseData[1]))
            except Exception as e:
                self.log.error("Failed to convert JSON to GPB: %s" % e.message)
            else:
                # Package response data into a message object
                response = ThalesZMQMessage(name=respName)
                response.body = respBody
                return response

        if responseData is None:
            self.log.error("Timeout waiting for response from %s" % self.address)
        else:
            self.log.warning("Malformed message received")
        # Return an empty response object
        return ThalesZMQMessage()
