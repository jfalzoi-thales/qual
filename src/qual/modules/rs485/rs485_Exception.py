from common.module.exception import ModuleException

## RS232 Module Exception
#
class RS485ModuleSerialException(ModuleException):
    def __init__(self, port):
        super(RS485ModuleSerialException, self).__init__()
        self.msg = 'Unable to open device %s.' % (port,)
