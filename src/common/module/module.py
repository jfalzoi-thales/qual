from threading import Thread
from time import sleep
import datetime

from common.logger.logger import Logger
from common.module.exception import ModuleException

## Module Base class
#
class Module(object):


    ## Class Method for returning configurations
    #
    # Modules that require/desire parameters passed to their constructors may
    # implement this function in their class.  The return value is a "list of dict",
    # each dictionary will be passed to the constructor for an instance of the module.
    # Therefore if multiple copies of the module are desired, a list of size >1 may
    # be created.
    #
    # @param cls Class, passed to classMethod
    #
    @classmethod
    def getConfigurations(cls):
        return [{"name": "default"},]


    ## Constructor
    #  @param     self
    #  @param     config Configuration data.  Stored here, but opague to this class
    def __init__(self, config):
        ## Used by threading methods to indicate the threads should keep running
        self.__running = False
        ## Stored configuration data, passed in by constructor
        self.config = config
        ## Name of module.  Defaults to class name, may be overwritten by self.setName()
        self.name = type(self).__name__
        ## List of messasage handlers, populated by self.addMsgHandler()
        self.msgHandlers = []
        ## List of managed threads, populated by self.addThread()
        self.threads = []
        ## Save the arguments for threads when they are configured, to use in their runtime constructions
        self.threadArgs = []

        self.log = Logger(self.name)

        return

    ## Changes the name of the module.
    #
    # The name of the module defaults to the class name and
    # is visible in the logging mechanisms
    # @param     self
    # @param     name  The new name of the module
    def setName(self, name):
        self.name = name
        return

    ## Changes the name of the module.
    #
    # Called to terminate the module.  Should be overwritten to perform
    # any implementation-specific cleanup.  If overwritten, the superclass
    # should be called.
    # @param     self
    def terminate(self):
        return

    ## Adds a message handler
    #
    # Registers this module as "interested" in receiving the messages of the
    # specified class.  Should be called in constructor.
    #
    # @param     self
    # @param     msgClass  The class of GPB being handled
    # @param     handler   A handler function (def <handlerName>(self, msg))
    def addMsgHandler(self, msgClass, handler):
        self.msgHandlers.append((msgClass, handler))
        return

    ## Calls the appropriate message handler
    #
    # Given a GPB message type, calls the appropriate message handler.
    # @todo : This is a unit test construct, QTA will call handlers directly.
    # @param     msg The message being procced.
    def msgHandler(self, msg):
        self.log.debug('Received %s\n%s' % (msg.body.__class__.__name__, msg.body.__str__()))
        for item in self.msgHandlers:
            if isinstance(msg.body, item[0]):
                retMsg = item[1](msg)
                self.log.debug('Sent %s\n%s' % (retMsg.body.__class__.__name__, retMsg.body.__str__()))
                return retMsg

        raise ModuleException('Thread %s %s msg handler not defined' %
                                          (self.name,msg.body.__class__.name,))




    #--------------Threading Funtions Below------------------

    ## Private function, calls the runMethod for each thread
    # @param self
    # @param     runMethod  The thread main function
    def _execute(self, runMethod):
        try:
            while self.__running:
                runMethod()

        except Exception as e:
            #TODO: Need to handle this
            raise

    ## Adds a Thread to the basic threading system, by specifying the thread's Main
    # @param self
    # @param runMethod The thread main function (def <main>(self))
    def addThread(self, runMethod):
        threadArgs = {
            'runMethod': runMethod,
        }
        self.threadArgs.append(threadArgs)
        return

    ## Starts all Threads registered with self.addThread()
    # @param self
    def startThread(self):

        if self.__running:
            raise ModuleException('Module %s is already running' % (self.name,))

        self.__running = True

        for threadArg in self.threadArgs:
            thread = Thread(target=self._execute, name=self.name, kwargs=threadArg)
            self.threads.append(thread)

        for thread in self.threads:
            if thread.isAlive():
                raise ModuleException('Thread %s already active' % (self.name,))
            thread.start()
        return

    ## stops all Threads registered with self.addThread()
    # @param self
    def stopThread(self):
        timeout = datetime.datetime.now() + datetime.timedelta(seconds=5)
        for thread in self.threads:
            while (thread.isAlive() == False):
                sleep(0.1)
                if datetime.datetime.now() > timeout:
                    raise ModuleException('Thread %s did not terminate' % (self.name,))

        self.threads = []
        self.__running = False

        return



