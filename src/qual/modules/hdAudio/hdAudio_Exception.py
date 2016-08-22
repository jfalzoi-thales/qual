from common.module.exception import ModuleException

## HDAudio Module Exception
class HDAudioModuleException(ModuleException):
    ## Constructor
    #  @param     self
    #  @param     msg  Message text associated with this exception
    def __init__(self, msg):
        super(HDAudioModuleException, self).__init__()
        ## Message text associated with this exception
        self.msg = msg
