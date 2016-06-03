import logging
from common.module.module import ModuleException
from common.logger.logger import Logger

## RS232 Module Exception
#
class RS232ModuleSerialException(ModuleException):
    def __init__(self, port):
        super(RS232ModuleSerialException, self).__init__()
        self.log = Logger(name='RS-232 Module', level=logging.DEBUG)
        self.log.error('Unable to open device %s.' % (port,))