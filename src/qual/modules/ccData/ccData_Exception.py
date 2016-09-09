from tklabs_utils.module.exception import ModuleException

## CarrierCardData Module Exception Class
class CarrierCardDataModuleException(ModuleException):
    ## Constructor
    #  @param     self
    #  @param     msg  Message text associated with this exception
    def __init__(self, msg):
        super(CarrierCardDataModuleException, self).__init__()
        ## Message text associated with this exception
        self.msg = msg
