
import zmq
import json
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.jsonConversion.jsonConversion import JsonConversion


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
        # Convert GPB response message to JSON
        try:
            reqName, reqJson = JsonConversion.gpb2json(request.body)
        except Exception as e:
            print "Failed to convert GPB to JSON:", e.message
            # Return an empty response object
            return ThalesZMQMessage()

        # JSON ZMQ message is a multipart message made up of string name and JSON body
        self.zsocket.send_multipart((reqName, json.dumps(reqJson)))

        # This will block waiting for the response
        responseData = self.zsocket.recv_multipart()

        # We expect JSON messages to have 2 parts
        if len(responseData) >= 2:
            # If message has more than 2 parts, log a warning, but proceed anyway
            if len(responseData) > 2:
                print "Warning: received response message with", len(responseData), "parts"

            # Response class name is in first part
            respName = str(responseData[0])

            # Convert JSON string to a GPB object
            try:
                respBody = JsonConversion.json2gpb(respName, json.loads(responseData[1]))
            except Exception as e:
                print "Failed to convert JSON to GPB:", e.message
            else:
                # Package response data into a message object
                response = ThalesZMQMessage(name=respName)
                response.body = respBody
                return response

        print "Malformed message received"
        # Return an empty response object
        return ThalesZMQMessage()
