
from threading import Thread, Lock
from common.configurableObject.configurableObject import ConfigurableObject
from common.tzmq.ThalesZMQServer import ThalesZMQServer
from common.tzmq.JsonZMQServer import JsonZMQServer
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
class QualTestApp(ConfigurableObject):
    ## Constructor
    # @param self
    def __init__(self):
        # Init the superclass
        super(QualTestApp, self).__init__(None)

        ## Logger implementation, based on standard python logger
        self.log = Logger(type(self).__name__)

        ## Address to use for GPB listener
        self.gpbServiceAddress = "tcp://*:50001"
        ## Address to use for JSON listener
        self.jsonServiceAddress = "tcp://*:50002"
        # Read config file and update specified instance variables
        self.loadConfig(attributes=('gpbServiceAddress','jsonServiceAddress'))

        ## Map of {<class>:[<instances>...]}
        self.__instances = {}

        ## All available classes in QUAL modules for QTA
        self.__modClasses = ClassFinder(rootPath='qual.modules',
                                        baseClass=Module)

        ## All available classes in GPB modules for QTA
        self.__gpbClasses = ClassFinder(rootPath='common.gpb.python',
                                        baseClass=Message)

        ## Lock for access to handler
        self.handlerLock = Lock()

        #  Create instances for each possible configuration
        for className in self.__modClasses.classmap.keys():
            _class = self.__modClasses.getClassByName(className)
            _config = _class.getConfigurations()
            for config in _config:
                if self.__instances.has_key(className):
                    try:
                        obj = _class(config)
                    except ModuleException as e:
                        self.log.error("Unable to create instance of %s: %s" % (className, e.msg,))
                    else:
                        self.log.info("Created instance of %s" % className)
                        self.__instances[className].append(obj)
                else:
                    try:
                        obj = _class(config)
                    except ModuleException as e:
                        self.log.error("Unable to create instance of %s: %s" % (className, e.msg,))
                    else:
                        self.log.info("Created instance of %s" % className)
                        self.__instances[className] = [obj]

        self.log.info("Initialization complete")

    ## Called by ZMQ handlers when a request is received from a client.
    #
    # @param request ThalesZMQMessage containing received request
    # @return        ThalesZMQMessage response to send back to the client
    def handleRequest(self, request):
        # Whole function is inside lock because both GPB and JSON servers use it
        self.handlerLock.acquire()

        # This will be the response we send back; set to None until someone handles the request
        response = None

        # Deserialize the message body if necessary
        if request.body is None:
            requestClass = self.__gpbClasses.getClassByName(request.name)
            if requestClass is None:
                self.log.warning("Unknown message class in request: %s" % request.name)
                response = ThalesZMQServer.getUnsupportedMessageErrorResponse()
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
            response = ThalesZMQServer.getUnsupportedMessageErrorResponse()

        # Whole function is inside lock because both GPB and JSON servers use it
        self.handlerLock.release()

        # Return the response so that it will get sent back to the client
        return response


## Class to set up a listener for GPB messages and hand them off to the main QTA class
class QtaGpbListener(ThalesZMQServer):
    ## Constructor
    # @param qtaInstance  The main QTA instance this will be linked to
    def __init__(self, qtaInstance):
        ## QTA instance we will be linked to
        self.qta = qtaInstance
        # Init the superclass
        super(QtaGpbListener, self).__init__(address=self.qta.gpbServiceAddress)

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage containing received request
    # @return        ThalesZMQMessage response to send back to the client
    def handleRequest(self, request):
        # Just hand off to the QTA request handler and return its response
        return self.qta.handleRequest(request)


## Class to set up a listener for JSON messages and hand them off to the main QTA class
class QtaJsonListener(JsonZMQServer):
    ## Constructor
    # @param qtaInstance  The main QTA instance this will be linked to
    def __init__(self, qtaInstance):
        ## QTA instance we will be linked to
        self.qta = qtaInstance
        # Init the superclass
        super(QtaJsonListener, self).__init__(address=self.qta.jsonServiceAddress)

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage containing received request
    # @return        ThalesZMQMessage response to send back to the client
    def handleRequest(self, request):
        # Just hand off to the QTA request handler and return its response
        return self.qta.handleRequest(request)


if __name__ == "__main__":
    # Create a QTA instance and the GPB and JSON listeners
    qta = QualTestApp()
    gpbListener = QtaGpbListener(qta)
    jsonListener = QtaJsonListener(qta)

    # Create a thread for the JSON listener
    thread = Thread(target=jsonListener.run, name="QtaJsonListener")
    thread.start()

    # Start the GPB listener running - function won't return
    gpbListener.run()
