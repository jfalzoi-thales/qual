import Queue
from threading import Thread
from time import sleep


class ExceptionModuleAbort(Exception):
    pass

class ModuleCtrlStop(object):
    pass

class Module(object):
    # currentConfig is class scope (shared across all Test)

    def __init__(self, config):
        self.config = config
        self.ctrlQ = Queue.Queue()
        self.name = type(self).__name__

        self.thread = Thread(target=self._execute,
                             name=self.name)
        self.thread.start()


    def terminate(self):

        print ("destructor")
        if self.thread.isAlive() == True:
            msg = ModuleCtrlStop()
            self.ctrlQ.put(msg)
            for loop in range(10) :
                if self.thread.isAlive() == False:
                    return
                sleep(1)
        raise Exception('Thread %s failed to close' % (self.name))


    ## Run a complete test case
    #
    def _execute(self):

        try:
            self.setup()
            try:
                while self._monitorCtrl():
                    self.run()
            except ExceptionModuleAbort as e:
                # this is already logged
                pass
            self.cleanup()
        except Exception as e:
            #TODO: Need to handle this
            raise

    def _monitorCtrl(self):
        # See if there are any pending exceptions from the child threads
        try:
            ctrlMsg = self.ctrlQ.get(block=False)
            if isinstance(ctrlMsg, ModuleCtrlStop) :
                return False

        except Queue.Empty:
            return True
        except Exception as e:
            raise


    def message(self, msg):
        pass

    ## Placeholder for virtual
    #@param params parameters given to execute method
    #
    def run(self):
        pass

    ## Placeholder for virtual
    #@param params parameters given to execute method
    #
    def setup(self):
        pass

    ## Placeholder for virtual
    #@param params parameters given to execute method
    #
    def cleanup(self):
        pass


    ## DEBUG is for information that will normally not be shown in any logs unless enabled
    DEBUG = 1
    INFO = 2
    WARNING =  3
    ERROR =  4
    CRITICAL =  5

    ## Add information to the test log
    #@param level One of DEBUG, INFO, WARNING, ERROR, CRITICAL
    #@param message Textual information to be added to the log
    #
    def log(self, level, message):
        print 'Log: %d %s' % (level, message)


    ## Test Assertion: logs that the given expression is boolean-true
    #
    #@param expression : Expression to be executed and compared against true
    #@param msg : additional log information
    def assertTrue(self, expression, msg):
        if expression is False:
            self.log (Module.CRITICAL, msg)
            raise ExceptionModuleAbort()




