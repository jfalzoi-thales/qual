import inspect
import logging
import logging.handlers
import socket
import sys
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

        ## Log level
        self.logLevel = 'INFO'
        ## Syslog address
        self.syslogAddress = 'localhost'
        ## Syslog port
        self.syslogPort = 514
        self.syslogLabel = 'mps-dev'

        # Default to local syslog on Linux because rsyslogd doesn't enable TCP/UDP logging by default
        if sys.platform.startswith('linux'):
            ## Syslog protocol
            self.syslogProtocol = 'local'
        else:
            ## Syslog protocol
            self.syslogProtocol = 'udp'

        if name is None:
            name = self._getCallerModule().__name__

        logging.getLoggerClass().__init__(self, name, level=self.logLevel)
        ConfigurableObject.__init__(self, name)

        self.loadConfig(attributes=('logLevel','syslogAddress','syslogPort','syslogProtocol','syslogLabel'))
        self._formatConsoleChannel()
        self._formatSyslogChannel()
        self.setLevel(self.logLevel)

    def setLevel(self, level):
        logLevels = {
            'NOTSET': logging.NOTSET,
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARN,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'FATAL': logging.FATAL,
            'CRITICAL': logging.CRITICAL,

        }

        value = None
        if isinstance(level, int) :
            value = level
        elif isinstance(level, str):
            if level.isdigit():
                value = int(level)
            elif level.upper() in logLevels.keys():
                value = logLevels[level.upper()]
        if value is None:
            self.error('Unknown Log Level %s not in %s ' % (str(level), logLevels.keys()))
            value = 0

        return logging.getLoggerClass().setLevel(self, level=value)




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

        if self.syslogProtocol.lower() == 'local':
            address = "/dev/log"
            socktype = socket.SOCK_DGRAM
        elif self.syslogProtocol.lower() == 'tcp':
            address = (self.syslogAddress, self.syslogPort)
            socktype = socket.SOCK_STREAM
        elif self.syslogProtocol.lower() == 'udp':
            address = (self.syslogAddress, self.syslogPort)
            socktype = socket.SOCK_DGRAM
        else:
            raise Exception('Unknown syslog protocol %s' %  (self.syslogProtocol))

        ch = logging.handlers.SysLogHandler(address=address, socktype=socktype)

        ch.setLevel(DEBUG)
        formatter = logging.Formatter('%s: %%(name)s - %%(message)s' % (self.syslogLabel,))
        ch.setFormatter(formatter)
        self.addHandler(ch)
