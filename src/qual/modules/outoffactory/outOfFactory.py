import subprocess
import os
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.pb2.OOF_pb2 import *

## Discard the output
DEVNULL = open(os.devnull, 'wb')

## OOF Module class
#
class Oof(Module):
    ## Constructor
    def __init__(self, config=None):
        # Init the parent class
        super(Oof, self).__init__(None)
        # adding the message handler
        self.addMsgHandler(OutOfFactoryRequest, self.handlerMessage)

    ## Called by base class when an OutOfFactoryRequest object is received from a client.
    #
    #  @param: oofRequest
    #  @type:  OutOfFactoryRequest obj
    def handlerMessage(self,oofRequest):
        # Create the empty response
        oofResponse = OutOfFactoryResponse()
        # Init with failure
        oofResponse.success = False
        # run the command, and catch the exception if it failed
        try:
            self.runMakeRaidOOF()
        except Exception:
            # if an error, success is already False
            pass
        else:
            oofResponse.success = True

        return ThalesZMQMessage(oofResponse)

    ## Runs a command, and can raise an exception if the command fails
    #  @param   self
    def runMakeRaidOOF(self):
        self.log.debug('Running: mpsinst-makeraid-oof')
        rc = subprocess.call('./mpsinst-makeraid-oof.sh 10 \"YES,CLEAR_MY_DISKS\" > /tmp/outoffactory.log 2>&1', shell=True)
        self.log.debug("Command return code: %d" % rc)
        if rc != 0:
            self.log.error('Unable to delete RAID volume')
            raise Exception()