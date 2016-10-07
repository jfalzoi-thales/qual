from tklabs_utils.module.exception import ModuleException

## SSD Module Exception
#
class SSDModuleException(ModuleException):
    ## Constructor
    #  @param     self
    #  @param     msg  Message text associated with this exception
    def __init__(self, msg):
        super(SSDModuleException, self).__init__()
        ## Message text associated with this exception
        self.msg = msg
