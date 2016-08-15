from common.module.exception import ModuleException

## Encoder Module Exception
#
class EncoderModuleSerialException(ModuleException):
    ## Constructor
    #  @param     self
    #  @param     port  Port associated with this exception
    def __init__(self, port):
        super(EncoderModuleSerialException, self).__init__()
        ## Message text associated with this exception
        self.msg = 'Unable to open device %s.' % (port,)