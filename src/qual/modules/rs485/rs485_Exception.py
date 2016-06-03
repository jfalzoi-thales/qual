import logging
from common.module.module import ModuleException
from common.logger.logger import Logger

## RS232 Module Exception
#
class RS485ModuleSerialException(ModuleException):
    def __init__(self, port):
        super(RS485ModuleSerialException, self).__init__()
        self.log = Logger(name='RS-485 Module', level=logging.DEBUG)
        self.log.error('Unable to open device %s.' % (port,))