
from common.tzmq.ThalesZMQServer import ThalesZMQServer
from common.logger.logger import Logger
from common.classFinder.classFinder import ClassFinder
from common.module.module import Module
from common.module.exception import ModuleException
from google.protobuf.message import Message


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
        for className in self.__modClasses.classmap.keys():
            _class = self.__modClasses.getClassByName(className)
            _config = _class.getConfigurations()
            for config in _config:
                if self.__instances.has_key(className):
                    try:
                        obj = _class(config)
                    except ModuleException as e:
                        self.log.error("Unable to create instance of %s, Error msg: %s" % (className, e.msg,))
                    else:
                        self.log.info("Created instance of %s" % className)
                        self.__instances[className].append(obj)
                else:
                    try:
                        obj = _class(config)
                    except ModuleException as e:
                        self.log.error("Unable to create instance of %s, Error msg: %s" % (className, e.msg,))
                    else:
                        self.log.info("Created instance of %s" % className)
                        self.__instances[className] = [obj]

        self.log.info("Initialization complete")

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage containing received request
    # @return        ThalesZMQMessage response to send back to the client
    def handleRequest(self, request):
        # This will be the response we send back; set to None until someone handles the request
        response = None

        # Deserialize the message body if necessary
        if request.body is None:
            requestClass = self.__gpbClasses.getClassByName(request.name)
            if requestClass is None:
                self.log.warning("Unknown message class in request: %s" % request.name)
                response = self.getUnsupportedMessageErrorResponse()
            else:
                # Create a GPB object of the correct message class and deserialize into it
                msg = requestClass()
                msg.ParseFromString(request.serializedBody)
                # Update the request
                request.body = msg

        if response is None:
            # Get the correct module
            for _module in self.__instances.itervalues():
                for modObject in _module:
                    for msgHandler in modObject.msgHandlers:
                        # If the message class matches one of the instances, pass the message
                        if msgHandler[0] == request.body.__class__:
                            # Get the ThalesZMQ response object
                            self.log.debug("Passing %s message to %s module" % (request.name, modObject.__class__.__name__))
                            response = modObject.msgHandler(request)
                            if response is not None:
                                break

        # If no module instance handled the request, return an error
        if response is None:
            self.log.warning("No handler for received message of class: %s" % request.name)
            response = self.getUnsupportedMessageErrorResponse()

        # Return the response so that it will get sent back to the client
        return response

if __name__ == "__main__":
    # Create a QTA instance and start it running
    qta = QualTestApp()
    qta.run()
