from common.module.module import ModuleException
from common.logger.logger import Logger, FATAL

## RS232 Module Exception
#
class HDAudioModuleException(ModuleException):
    def __init__(self, msg):
        super(HDAudioModuleException, self).__init__()
        self.msg = msg
        self.log = Logger(name='HD Audio Module', level=FATAL)
        self.log.error(self.msg)