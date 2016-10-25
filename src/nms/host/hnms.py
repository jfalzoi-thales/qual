import os
import subprocess
from systemd.daemon import notify as sd_notify

from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.module.moduleshell import ModuleShell
from tklabs_utils.tzmq.ThalesZMQServer import ThalesZMQServer
from tklabs_utils.vtss.vtss import Vtss

## Discard the output
DEVNULL = open(os.devnull, 'wb')

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
        # Get BIOS info
        biosInfo = self.getBiosInfo()
        self.moduleShell.log.info(biosInfo)
        # Get i350_eeprom and i350_PXE Firmware
        i350Info = self.geti350Info()
        self.moduleShell.log.info(i350Info[0])
        self.moduleShell.log.info(i350Info[1])
        # Get the switch information
        switchInfo = self.getSwitchInfo()
        self.moduleShell.log.info(switchInfo[0])
        self.moduleShell.log.info(switchInfo[1])

    ## Get the info from the Vitesse Ethernet Switch
    #
    #  @return: (version,config_version)
    #  @type: tuple(str, str)
    def getSwitchInfo(self):
        # In case we can't get the info, "not found." will be logged
        firmwareInfo = "Not found."
        configInfo = "Not found."
        # Open connection with the switch
        vtss = Vtss(switchIP=self.switchAddress)
        # Get the info from the switch
        jsonResp = vtss.callMethod(['firmware.status.switch.get'])
        # If no error, update the info
        if jsonResp['error'] == None:
            firmwareInfo = jsonResp['result'][0]['val']['Version']

        # Get the config info
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
                        configInfo = lines[index-1]

        return ('version.switch='+firmwareInfo, 'version.switch_config='+configInfo)

    ## Get the i350_eeprom and i350_PXE Firmware
    #
    #  @return: (i350_eeprom,i350_PXE Firmware)
    #  @type: tuple(str, str)
    def geti350Info(self):
        # In case we can't get the info, "not found." will be logged
        i350_eeprom = 'Not found.'
        i350_pxe = 'Not found.'

        # Get EEPROM
        eePromValue = self._readWord(0x10)
        # If success
        if eePromValue != None:
            majorVersion = str((eePromValue & 0xf000) >> 12)
            minorVersion = str(eePromValue & 0xff)
            eePromValue =  self._readWord(0x12)
            if eePromValue != None:
                oem = str(eePromValue)
                # If we reach this point, we have the major and the minor version, and the OEM
                # We can update the response for EEPROM
                i350_eeprom = '%s.%s.%s' % (majorVersion,minorVersion,oem)

        # Get i350 firmware version
        i350firmware = self._readWord(0x64)
        if i350firmware != None:
            majorVersion = str((i350firmware & 0xf000) >> 12)
            minorVersion = str(i350firmware & 0xf00) >> 8
            buildNumber = str(i350firmware & 0xff)
            # If we reach this point, we have the major and the minor version, and the OEM
            # We can update the response for i350 Firmware version
            i350_pxe = '%s.%s.%s' % (majorVersion,minorVersion,buildNumber)


        return ('version.i350_eeprom='+i350_eeprom, 'version.i350_pxe='+i350_pxe)

    ## Get BIOS information
    #  @return: biosInfo
    #  @type: str
    def getBiosInfo(self):
        # In case we can't get the info, "not found." will be logged
        biosInfo = 'Not found.'
        # get information
        proc = subprocess.Popen(['amidewrap' ,'/SS', '/SV'],stdout=subprocess.PIPE)
        proc.wait()
        if proc.returncode != 0:
            self.moduleShell.log.error('Unable to retrieve BIOS information.')
        else:
            lines = proc.stdout.readlines()
            for line in lines:
                if 'System version' in line:
                    line = line.split(" ")
                    biosInfo = line[-1]

        return 'version.BIOS='+biosInfo

    ## Private function
    #
    #  @param: offset
    def _readWord(self, offset):
        # Device
        ethDevice = 'ens1f0'
        if subprocess.call(['ethtool', ethDevice], stdout=DEVNULL, stderr=DEVNULL) != 0:
            self.moduleShell.log.error('Unable to acces i350 device ens1f0')
            return None
        else:
            # Call ethtool to read the word at the specified offset
            cmd = ['ethtool', '-e', ethDevice, 'offset', str(offset), 'length', '2', 'raw', 'on']
            ethtool = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            data = ethtool.stdout.read(2)
            rc = ethtool.wait()
            if rc != 0:
                return None
        # Values are stored little-endian
        val = (ord(data[1]) << 8) | ord(data[0])

        return val


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
