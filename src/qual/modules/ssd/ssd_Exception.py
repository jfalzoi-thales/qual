from common.logger.logger import Logger, FATAL
from common.module.exception import ModuleException

class SSDDeviceException(ModuleException):
    def __init__(self, device):
        super(SSDDeviceException, self).__init__()
        self.msg = 'Device missing: %s' % (device,)
        self.log = Logger(name='SSD Module', level=FATAL)
        self.log.error(self.msg)