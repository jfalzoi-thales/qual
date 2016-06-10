
import zmq
import json
from common.logger.logger import Logger
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.tzmq.ThalesZMQServer import ThalesZMQServer
from common.gpb.jsonConversion.jsonConversion import JsonConversion


## JSON ZMQ Server class
#
# Binds to a ZMQ socket and accepts messages that uses the JSON-over-ZMQ
# protocol as defined by the "MPS Qualification Software ICD" and allows
# receiving requests and sending responses (REQ-REP ZMQ pattern).
class JsonZMQServer(object):
    ## Constructor
    #
    # @param address ZMQ address string for socket to bind to
    def __init__(self, address):
        ## Logger implementation, based on standard python logger
        self.log = Logger(type(self).__name__)
        ## ZMQ address for socket to bind to
        self.address = address
        ## ZMQ context
        self.zcontext = zmq.Context.instance()
        ## ZMQ socket
        self.zsocket = self.zcontext.socket(zmq.REP)
        self.zsocket.bind(self.address)
        self.log.info("Listening for JSON requests on %s" % self.address)

    ## Starts up a loop that handles requests.
    #
    # Will only return if canceled (e.g. Ctrl-C).
    def run(self):
        while True:
            # This will block waiting for a request
            try:
                requestData = self.zsocket.recv_multipart()
            except KeyboardInterrupt:
                return

            # Return this if something goes wrong
            respName, respJson = self.getUnsupportedMessageErrorResponse()

            # We expect JSON messages to have 2 parts
            if len(requestData) >= 2:
                # If message has more than 2 parts, log a warning, but proceed anyway
                if len(requestData) > 2:
                    self.log.error("Received JSON message with %d parts" % len(requestData))

                # Request class name is in first part
                reqName = str(requestData[0])
                self.log.debug("Received JSON %s:\n%s" % (reqName, requestData[1]))

                # Convert JSON to a GPB object
                try:
                    reqBody = JsonConversion.json2gpb(reqName, json.loads(requestData[1]))
                except Exception as e:
                    self.log.error("Failed to convert JSON to GPB: %s" % e.message)
                else:
                    # Package request data into a ThalesZMQMessage object
                    request = ThalesZMQMessage(name=reqName)
                    request.body = reqBody

                    # Hand the request off to to HandleRequest(), which will return the response
                    response = self.handleRequest(request)

                    # Convert GPB response message to JSON
                    try:
                        respName, respJson = JsonConversion.gpb2json(response.body)
                    except Exception as e:
                        self.log.error("Failed to convert GPB to JSON: %s" % e.message)

            else:
                self.log.error( "Malformed message received; ignoring")
                respName, respJson = self.getMalformedMessageErrorResponse()

            # Send the response message back to the client.
            # JSON ZMQ message is a multipart message made up of string name and JSON body.
            jsonStr = json.dumps(respJson)
            self.log.debug("Sending JSON %s:\n%s" % (respName, jsonStr))
            self.zsocket.send_multipart((respName, jsonStr))

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
        return ThalesZMQServer.getUnsupportedMessageErrorResponse()

    ## Returns an error response message
    #
    # @param code Numeric error code
    # @param description Text description of error
    # @return (name, JSON) tuple containing ErrorMessage
    @staticmethod
    def getErrorResponse(code, description):
        # Build JSON manually rather than rely on JsonConversion class because this can't fail
        return "ErrorMessage", {"error_code": code, "error_description": description}

    ## Returns an error response message of type "Unsupported message"
    #
    # @return (name, JSON) tuple containing ErrorMessage
    @staticmethod
    def getUnsupportedMessageErrorResponse():
        # Note: This error code was taken from the HDDS ICD; may not be correct usage
        return JsonZMQServer.getErrorResponse(1000, "Unsupported message received")

    ## Returns an error response message of type "Malformed message"
    #
    # @return (name, JSON) tuple containing ErrorMessage
    @staticmethod
    def getMalformedMessageErrorResponse():
        # Note: This error code was taken from the HDDS ICD; may not be correct usage
        return JsonZMQServer.getErrorResponse(1000, "Malformed message received")
