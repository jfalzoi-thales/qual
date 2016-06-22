import inspect
import logging
import logging.handlers
import socket
from common.configurableObject.configurableObject import ConfigurableObject

CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET


#Level	    When it is used
#DEBUG	    Detailed information, typically of interest only when diagnosing problems.
#INFO	    Confirmation that things are working as expected.
#WARNING	An indication that something unexpected happened,
#           or indicative of some problem in the near future (e.g. disk space low).
#           The software is still working as expected.
#ERROR	    Due to a more serious problem, the software has not been able to perform some function.
#CRITICAL	A serious error, indicating that the program itself may be unable to continue running.

## Logger Class
#
# The logger class is derived from the standard logger.
# @see https://docs.python.org/2/howto/logging.html#logging-basic-tutorial
# We use this implementation to centralize, and so that we can add new
# Channels that are log level based (for example we could add some levels
# to the syslog, or send an email, or whatever we want (add stack trace for errors)
#
# Examples
# log = Logger(self.name)
# log.debug('debug message')
# log.info('info message')
# log.warn('warn message')
# log.error('error message')
# log.critical('critical message')
class Logger(logging.getLoggerClass(), ConfigurableObject):

    ## Constructor
    #  @param     name  The name of the debug channel, if not set will be the caller's module name
    def __init__(self, name=None):

        self.logLevel = INFO
        self.syslogAddress = 'localhost'
        self.syslogPort = 514
        self.syslogProtocol = 'udp'

        if name is None:
            name = self._getCallerModule().__name__

        logging.getLoggerClass().__init__(self, name, level=self.logLevel)
        ConfigurableObject.__init__(self, name)

        self.loadConfig(attributes=('logLevel','syslogAddress','syslogPort','syslogProtocol',))
        self._formatConsoleChannel()
        self._formatSyslogChannel()
        self.setLevel(self.logLevel)

    # Gets the caller's module name as a default logger name
    def _getCallerModule(self):
        frm = inspect.stack()[2]
        module = inspect.getmodule(frm[0])
        return module

    # Formats a console channel
    def _formatConsoleChannel(self):
        ch = logging.StreamHandler()
        ch.setLevel(DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.addHandler(ch)

    # Formats a syslog channel
    def _formatSyslogChannel(self):

        if self.syslogProtocol.lower() == 'tcp':
            socktype = socket.SOCK_STREAM
        if self.syslogProtocol.lower() == 'udp':
            socktype = socket.SOCK_DGRAM
        else:
            raise Exception('Unknown syslog protocol %s' %  (self.syslogProtocol))

        ch = logging.handlers.SysLogHandler(address=(self.syslogAddress, self.syslogPort),socktype=socktype)

        ch.setLevel(DEBUG)
        formatter = logging.Formatter('%(name)s - %(message)s')
        ch.setFormatter(formatter)
        self.addHandler(ch)
