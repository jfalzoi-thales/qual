
from common.tzmq.ThalesZMQServer import ThalesZMQServer


## Qual Test Application Class
#
# This class:
#  - Provides the Thales ZMQ REQ-REP network socket for the TE to connect to
#  - Discovers and loads all test module packages
#  - Creates module instances based on module static configuration
#  - Receives Thales ZMQ messages and routes to appropriate module instance
#  - For each incoming message, sends a response is sent back over ZMQ to the caller
#
class QualTestApp(ThalesZMQServer):
    ## Constructor
    #
    def __init__(self):
        # FIXME: Requirements don't state what TCP port to use for QTA, so this is arbitrary
        super(QualTestApp, self).__init__("tcp://*:50001")

        # TODO: Put GPB class loading (ClassFinder) stuff here

        # TODO: Put module discovery and instance creation here


    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleRequest(self, request):
        # Route messages based on type

        # TODO: Use ClassFinder to map request.name to a GPB class and deserialize request.body
        # If ClassFinder does not find a match, send reply message using:
        #    self.sendUnsupportedMessageErrorResponse()
        # If ClassFinder does find a match:
        #    Create an object of that class:         msgBody = MatchedClass()
        #    Deserialize the body into that object:  msgBody.ParseFromString(request.serializedBody)
        #    Update the request with the new object: request.body = msgBody

        # TODO: Route the deserialized message to a module instance
        # Next look up message class in registered modules list and
        # pass request to each matching module instance in sequence,
        # as described in "QAL Module Design" document.

        # TODO: Send reply back over ZMQ
        # If module instance handles a message, it will return a response message
        # and you can call this to send the response back over ZMQ:
        #    self.sendResponse(response)
        # If no module instance handles a request, call:
        self.sendUnsupportedMessageErrorResponse()

if __name__ == "__main__":
    # Create a QTA instance and start it running
    qta = QualTestApp()
    qta.run()
