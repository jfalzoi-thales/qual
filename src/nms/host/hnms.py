import os
from systemd.daemon import notify as sd_notify

from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.module.moduleshell import ModuleShell
from tklabs_utils.tzmq.ThalesZMQServer import ThalesZMQServer
from tklabs_utils.vtss.vtss import Vtss


## Host NMS Class
# Uses a ModuleShell to initialize modules and route messages to them
class HNMS(ConfigurableObject):
    ## Constructor
    # @param self
    def __init__(self):
        # Init the superclass
        super(HNMS, self).__init__()
        ## Address to use for GPB listener
        self.serviceAddress = "ipc:///tmp/nms.sock"
        ## Current version information from the Vitesse Ethernet Switch
        self.switchAddress = '10.10.41.159'
        #  Read config file and update specified instance variables
        self.loadConfig(attributes=('serviceAddress','switchAddress'))
        ## Module shell that will contain the modules
        self.moduleShell = ModuleShell(name="HNMS", moduleDir="nms.host.modules", messageDir="nms.host.pb2")
        switchInfo = self.getSwitchInfo()
        self.moduleShell.log.info("Switch Firmware: %s" % switchInfo[0])
        self.moduleShell.log.info("Config: %s" % switchInfo[1])

    ## Get the info from the Vitesse Ethernet Switch
    #
    def getSwitchInfo(self):
        # In case we can't get the info, "not found" will be logged
        firmwareInfo = "Not found."
        vtss = Vtss(switchIP=self.switchAddress)
        # Get the info from the switch
        jsonResp = vtss.callMethod(['firmware.status.switch.get'])
        # If no error, update the info
        if jsonResp['error'] == None:
            firmwareInfo = jsonResp['result'][0]['val']['Version']

        # Get the config info
        configInfo = "Not found"
        # Save the startup-config file
        jsonResp = vtss.callMethod(['icfg.control.copy.set','{"Argument1":{"Copy":true,"SourceConfigType":"2","SourceConfigFile":"flash:startup-config","DestinationConfigType":"3","DestinationConfigFile":"tftp://192.168.1.122/tmp-startup-config","Merge":false}}'])
        # If no error from the RPC, check if the file was actually copied
        if jsonResp['error'] == None:
            # If the file exist
            if os.path.exists('/thales/qual/firmware/tmp-startup-config'):
                # Read the file, and the config info is the line after the line "end"
                configFile = open('/thales/qual/firmware/tmp-startup-config')
                lines = configFile.readlines()
                # read the file backwards for optimization
                for index,line in reversed(list(enumerate(lines))):
                    if 'end' in line:
                        configInfo = lines[index+1]

        return (firmwareInfo, configInfo)


## Class to set up a listener for GPB messages and hand them off to the HNMS class
class HnmsGpbListener(ThalesZMQServer):
    ## Constructor
    # @param hnms  The main HNMS instance this will be linked to
    def __init__(self, hnms):
        ## HNMS instance we will be linked to
        self.hnms = hnms
        # Init the superclass
        super(HnmsGpbListener, self).__init__(address=hnms.serviceAddress, allowNoBody=True)

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage containing received request
    # @return        ThalesZMQMessage response to send back to the client
    def handleRequest(self, request):
        # Just hand off to the HNMS request handler and return its response
        return self.hnms.moduleShell.handleRequest(request)


## Main function for Host Network Management Service
def main():
    ConfigurableObject.setFilename("HNMS")
    # Create a HNMS instance and the GPB listener
    hnms = HNMS()
    gpbListener = HnmsGpbListener(hnms)

    sd_notify('READY=1')
    # Start the GPB listener running - function will only return on KeyboardInterrupt
    gpbListener.run()

    sd_notify('STOPPING=1')
    # Terminate moduleShell so we can exit cleanly
    hnms.moduleShell.terminate()

    # Return exit code for HNMS wrapper script
    return 0


if __name__ == '__main__':
    main()
