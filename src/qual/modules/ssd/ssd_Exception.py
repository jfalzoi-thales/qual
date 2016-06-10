from common.logger.logger import Logger, FATAL
from common.module.exception import ModuleException

class SSDModuleException(ModuleException):
    def __init__(self, msg):
        super(SSDModuleException, self).__init__()
        self.msg = msg
        self.log = Logger(name='SSD Module', level=FATAL)
        self.log.error(self.msg)