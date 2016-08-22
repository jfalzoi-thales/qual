from common.configurableObject.configurableObject import ConfigurableObject
from common.module.moduleshell import ModuleShell
from common.tzmq.ThalesZMQServer import ThalesZMQServer


## Host NMS Class
# Uses a ModuleShell to initialize modules and route messages to them
class HNMS(ConfigurableObject, ModuleShell):
    ## Constructor
    # @param self
    def __init__(self):
        # Init the superclass
        super(HNMS, self).__init__(moduleDir="host/modules", messageDir="host/pb2")


## Class to set up a listener for GPB messages and hand them off to the HNMS class
class HnmsGpbListener(ThalesZMQServer):
    ## Constructor
    # @param hnmsInstance  The main HNMS instance this will be linked to
    def __init__(self, hnmsInstance):
        ## HNMS instance we will be linked to
        self.hnms = hnmsInstance
        # Init the superclass
        super(HnmsGpbListener, self).__init__(address="ipc:///tmp/nms.sock")

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage containing received request
    # @return        ThalesZMQMessage response to send back to the client
    def handleRequest(self, request):
        # Just hand off to the HNMS request handler and return its response
        return self.hnms.handleRequest(request)


def main():
    # Create a HNMS instance and the GPB listener
    hnms = HNMS()
    gpbListener = HnmsGpbListener(hnms)

    # Start the GPB listener running - function will only return on KeyboardInterrupt
    gpbListener.run()

    # Terminate HNMS so we can exit cleanly
    hnms.terminate()
