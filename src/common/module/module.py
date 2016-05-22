import Queue
from threading import Thread
from time import sleep

import signal

import datetime

from src.common.gpb.python.baseMessage import BaseMessage


class ModuleException(Exception):
    pass


class Module(object):

    def __init__(self):
        self.__running = False
        self.name = type(self).__name__
        self._thread = Thread(target=self._execute, name=self.name)
        self.msgHandlers = []

    def start(self, msg):
        if self._thread.isAlive() == True:
            raise ModuleException('Thread %s already active' % (self.name,))
        self.__running = True
        self._thread.start()
        return

    def stop(self, msg):
        self.__running = False
        timeout = datetime.datetime.now() + datetime.timedelta(seconds=5)
        while(self._thread.isAlive() == False) :
            sleep(0.1)
            if datetime.datetime.now()  > timeout :
                raise ModuleException('Thread %s did not terminate' % (self.name,))
        return

    def addMsgHandler(self, msgClass, handler):
        self.msgHandlers.append((msgClass, handler))
        pass

    def msgHandler(self, msg):
        self.log('%s->%s' % (msg.__class__.__name__, msg.__str__()))
        for item in self.msgHandlers:
            if isinstance(msg, item[0]):
                retMsg = item[1](msg)
                if not isinstance(retMsg, BaseMessage) :
                    raise ModuleException('Thread %s %s msg handler type exception' %
                                          (self.name,msg.__class__.name,))
                self.log('%s<-%s' % (retMsg.__class__.__name__, retMsg.__str__()))
                return retMsg





    ##--------------Base Class Funtions Below

    ## Placeholder for virtual
    #@param params parameters given to execute method
    #
    def run(self):
        pass


    ## Add information to the test log
    #@param message Textual information to be added to the log
    #
    def log(self,  message):
        print 'Log: %s' % (message)


    def _execute(self):

        try:
            while self.__running:
                self.run()

        except Exception as e:
            #TODO: Need to handle this
            raise



