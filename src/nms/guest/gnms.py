from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.module.moduleshell import ModuleShell
from tklabs_utils.tzmq.ThalesZMQServer import ThalesZMQServer


## Guest NMS Class
# Uses a ModuleShell to initialize modules and route messages to them
class GNMS(ConfigurableObject):
    ## Constructor
    # @param self
    def __init__(self):
        # Init the superclass
        super(GNMS, self).__init__()
        ## Address to use for GPB listener
        self.serviceAddress = "tcp://*:40006"
        #  Read config file and update specified instance variables
        self.loadConfig(attributes=('serviceAddress',))
        ## Module shell that will contain the modules
        self.moduleShell = ModuleShell(name="GNMS", moduleDir="nms.guest.modules", messageDir="nms.guest.pb2")


## Class to set up a listener for GPB messages and hand them off to the GNMS class
class GnmsGpbListener(ThalesZMQServer):
    ## Constructor
    # @param gnms  The main GNMS instance this will be linked to
    def __init__(self, gnms):
        ## GNMS instance we will be linked to
        self.gnms = gnms
        # Init the superclass
        super(GnmsGpbListener, self).__init__(address=gnms.serviceAddress, allowNoBody=True)

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage containing received request
    # @return        ThalesZMQMessage response to send back to the client
    def handleRequest(self, request):
        # Just hand off to the GNMS request handler and return its response
        return self.gnms.moduleShell.handleRequest(request)


## Main function for Guest Network Management Service
def main():
    ConfigurableObject.setFilename("GNMS")
    # Create a GNMS instance and the GPB listener
    gnms = GNMS()
    gpbListener = GnmsGpbListener(gnms)

    # Start the GPB listener running - function will only return on KeyboardInterrupt
    gpbListener.run()

    # Terminate moduleShell so we can exit cleanly
    gnms.moduleShell.terminate()

    # Return exit code for GNMS wrapper script
    return 0


if __name__ == '__main__':
    main()
