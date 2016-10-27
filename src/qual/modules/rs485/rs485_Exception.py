from tklabs_utils.module.exception import ModuleException

## RS232 Module Exception
#
class RS485ModuleSerialException(ModuleException):
    ## Constructor
    #  @param     self
    #  @param     port  Port associated with this exception
    def __init__(self, port):
        super(RS485ModuleSerialException, self).__init__()
        ## Message text associated with this exception
        self.msg = 'Unable to open device %s.' % (port,)
