from tklabs_utils.module.exception import ModuleException

## Exception for this Module
#
class ConfigPortStateException(ModuleException):
    def __init__(self, msg):
        super(ConfigPortStateException, self).__init__()
        ## Text message associated with this exception
        self.msg = msg
