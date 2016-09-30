import subprocess
import os
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.pb2.SSDErase_pb2 import *

## Discard the output
DEVNULL = open(os.devnull, 'wb')

## SSDErase Module class
#
class SSDErase(Module):
    ## Constructor
    def __init__(self, config=None):
        # Init the parent class
        super(SSDErase, self).__init__(None)
        # adding the message handler
        self.addMsgHandler(SSDEraseRequest, self.handlerMessage)

    ## Called by base class when an SSDEraseRequest object is received from a client.
    #
    #  @param: SSDEraseRequest
    #  @type:  OutOfFactoryRequest obj
    def handlerMessage(self,ssdEraseRequest):
        # Create the empty response
        ssdEraseResponse = SSDEraseResponse()
        # Init with failure
        ssdEraseResponse.success = True
        if ssdEraseRequest.body.erase:
            # run the command, and catch the exception if it failed
            try:
                self.unmountIfMounted("/mnt/qual")
                self.unmountIfMounted("/tsp-download")
                self.runDestroyRaid()
            except Exception:
                ssdEraseResponse.success = False
                ssdEraseResponse.errorMessage = 'Unable to delete RAID volume'
            else:
                ssdEraseResponse.success = True

        return ThalesZMQMessage(ssdEraseResponse)

    ## Runs a command, and can raise an exception if the command fails
    #  @param   self
    def runDestroyRaid(self):
        self.log.debug('Running: mpsinst-destroyraid')
        rc = subprocess.call('/thales/host/appliances/mpsinst-destroyraid 10 \"YES,CLEAR_MY_DISKS\" > /tmp/destroyraid.log 2>&1', shell=True)
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
