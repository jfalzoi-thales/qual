
from common.tzmq.ThalesZMQServer import ThalesZMQServer
from common.logger.logger import Logger
from common.classFinder.classFinder import ClassFinder
from common.module.module import Module
from google.protobuf.message import Message


## Map to the

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
    # @attrib : modInstances The map of {<class>:[<instances>...]}
    # @attrib : module Classes
    # @attrib : gpb Classes
    def __init__(self, ip='*', port=50001):
        self.__instances = {}

        #  Address to be bended
        address = str.format('tcp://{}:{}',ip, port)
        super(QualTestApp, self).__init__(address=address)

        # Set up a logger
        self.log = Logger(name='QTA')

        #  All available classes in QUAL modules for QTA,
        self.__modClasses = ClassFinder(rootPath='qual.modules',
                                        baseClass=Module)

        #  All available classes in GPB modules for QTA,
        self.__gpbClasses = ClassFinder(rootPath='common.gpb.python',
                                        baseClass=Message)

        #  Create instances for each possible configuration
        for className in self.__modClasses.messageMap.keys():
            _class = self.__modClasses.getClassByName(className)
            _config = _class.getConfigurations()
            for config in _config:
                self.log.info("Created instance of %s" % className)
                if self.__instances.has_key(className):
                    self.__instances[className].append(_class(config))
                else:
                    self.__instances[className] = [_class(config)]

        self.log.info("Initialization complete")

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleRequest(self, request):
        # Route messages based on type
        requestClass = self.__gpbClasses.getClassByName(request.name)
        if requestClass is None:
            self.log.warning("Unknown message class in request: %s" % request.name)
            self.sendUnsupportedMessageErrorResponse()
        else:
            #  Create the message to pass to the module instances
            msg = requestClass()
            msg.ParseFromString(request.serializedBody)
            #  Update the request
            request.body = msg
            #   Get the correct module
            msgProcessed = False
            for _module in self.__instances.itervalues():
                for modObjet in _module:
                    for msgHandler in modObjet.msgHandlers:
                        #  if the message class matches one of the instances, pass the message
                        if msgHandler[0] == msg.__class__:
                            #  Get the ThalesZMQ response object
                            self.log.debug("Passing %s message to %s module" % (request.name, modObjet.__class__.__name__))
                            response = modObjet.msgHandler(request)
                            if response is not None:
                                self.sendResponse(response=response)
                                msgProcessed = True
            #  If no module instance handled the request, send en error
            if not msgProcessed:
                self.log.warning("No handler for received message of class: %s" % request.name)
                self.sendUnsupportedMessageErrorResponse()

if __name__ == "__main__":
    # Create a QTA instance and start it running
    qta = QualTestApp()
    qta.run()
