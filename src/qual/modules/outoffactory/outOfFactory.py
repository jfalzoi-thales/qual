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
            self.unmountIfMounted("/mnt/qual")
            self.unmountIfMounted("/tsp-download")
            self.runDestroyRaid()
        except Exception:
            # if an error, success is already False
            pass
        else:
            oofResponse.success = True

        return ThalesZMQMessage(oofResponse)

    ## Runs a command, and can raise an exception if the command fails
    #  @param   self
    def runDestroyRaid(self):
        self.log.debug('Running: mpsinst-destroyraid')
        rc = subprocess.call('mpsinst-destroyraid 10 \"YES,CLEAR_MY_DISKS\" > /tmp/destroyraid.log 2>&1', shell=True)
        self.log.debug("Command return code: %d" % rc)
        if rc != 0:
            self.log.error('Unable to delete RAID volume')
            raise Exception()

    ## Unmount a filesystem if mounted, and raise exception if it cannot be unmounted
    #  @param   self
    #  @param   fs        Device name or mount point of filesystem to search for
    def unmountIfMounted(self, fs):
        self.log.debug("Checking if filesystem %s is mounted" % fs)
        output = subprocess.check_output('mount | fgrep %s || true' % fs, shell=True)
        isMounted = output != ''
        if isMounted:
            if subprocess.call(['umount', fs]) != 0:
                self.log.error("Unable to unmount %s" % fs)
                raise Exception()
