from common.module.exception import ModuleException

## HDAudio Module Exception
#
class HDAudioModuleException(ModuleException):
    def __init__(self, msg):
        super(HDAudioModuleException, self).__init__()
        self.msg = msg
