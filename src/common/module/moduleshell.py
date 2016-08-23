from threading import Lock
from common.logger.logger import Logger
from common.classFinder.classFinder import ClassFinder
from common.module.module import Module
from common.module.exception import ModuleException
from google.protobuf.message import Message
from common.tzmq.ThalesZMQServer import ThalesZMQServer


## Module Shell Class
#
# This class:
#  - Discovers and loads all module packages
#  - Creates instances of each module
#  - Creates a table of message types handled by each module
#  - Receives Thales ZMQ messages and routes to appropriate module instance
#
class ModuleShell(object):
    ## Constructor
    # @param self
    # @param moduleDir  Directory to scan for module classes
    # @param messageDir Directory to scan for GPB message classes
    def __init__(self, moduleDir, messageDir):
        # Init the superclass
        super(ModuleShell, self).__init__()
        ## Logger implementation, based on standard python logger
        self.log = Logger(type(self).__name__)
        ## Directory to scan for module classes
        self.moduleDir = moduleDir
        ## Directory to scan for GPB message classes
        self.messageDir = messageDir
        ## Map of {<class>:<module instance>}
        self.__instances = {}
        ## All available module classes
        self.__modClasses = ClassFinder(rootPath=self.moduleDir, baseClass=Module)
        ## All available GPB message classes
        self.__gpbClasses = ClassFinder(rootPath=self.messageDir, baseClass=Message)
        ## Lock for access to handler
        self.handlerLock = Lock()

        #  Create instances for each possible configuration
        for className in self.__modClasses.classmap.keys():
            _class = self.__modClasses.getClassByName(className)
            try:
                obj = _class()
            except ModuleException as e:
                self.log.error("Unable to create instance of %s: %s" % (className, e.msg))
            else:
                self.log.info("Created instance of %s" % className)
                self.__instances[className] = obj

        self.log.info("Initialization complete")

    ## Terminate all modules so we can exit cleanly
    def terminate(self):
        for _module in self.__instances.itervalues():
            self.log.info("Terminating %s" % _module.__class__.__name__)
            _module.terminate()

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
                for msgHandler in _module.msgHandlers:
                    # If the message class matches one of the instances, pass the message
                    if msgHandler[0] == request.body.__class__:
                        # Get the ThalesZMQ response object
                        self.log.debug("Passing %s message to %s module" % (request.name, _module.__class__.__name__))
                        response = _module.msgHandler(request)
                        break

        # If no module handled the request, return an error
        if response is None:
            self.log.warning("No handler for received message of class: %s" % request.name)
            response = ThalesZMQServer.getUnsupportedMessageErrorResponse()

        # Whole function is inside lock because both GPB and JSON servers use it
        self.handlerLock.release()

        # Return the response so that it will get sent back to the client
        return response
