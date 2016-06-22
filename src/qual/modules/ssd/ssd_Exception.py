from common.module.exception import ModuleException

## SSD Module Exception
#
class SSDModuleException(ModuleException):
    def __init__(self, msg):
        super(SSDModuleException, self).__init__()
        self.msg = msg
