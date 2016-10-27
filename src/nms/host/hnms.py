import os
import socket
from subprocess import Popen, call, check_output, CalledProcessError, PIPE
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
        ## Name of CPU Ethernet device
        self.cpuEthernetDev = "enp0s31f"
        ## Name of I350 Ethernet device
        self.i350EthernetDev = "ens1f"
        #  Read config file and update specified instance variables
        self.loadConfig(attributes=('serviceAddress','switchAddress','cpuEthernetDev','i350EthernetDev'))
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
        # Get CPU MAC address
        cpuMAC = self.getNicMac(self.cpuEthernetDev)
        self.moduleShell.log.info(cpuMAC)
        # Get i350 MAC addresses
        for x in range(1, 4):
            i350MAC = self.getNicMac(self.i350EthernetDev + "_%s" % x)
            self.moduleShell.log.info(i350MAC)
        # Get switch MAC address
        switchMAC = self.getVtssMac()
        self.moduleShell.log.info(switchMAC)

    ## Get local Ethernet MAC addresses
    #  @param   self
    #  @param   device      Device who's MAC address is being retrieved
    def getNicMac(self, device):
        try:
            mac = check_output(["cat", "/sys/class/net/%s/address" % device])
        except CalledProcessError:
            mac = ""

        if not mac: self.moduleShell.log.error("Unable to retrieve MAC address for device: %s" % device)
        return "mac_address.%s=" % device + mac

    ## Get switch MAC addresses
    #  @param   self
    def getVtssMac(self):
        try:
            vtss = Vtss(self.switchAddress)
            json = vtss.callMethod(["ip.status.interface.link.get"])
            mac = json["result"][0]["val"]["macAddress"]
        except (socket.error, KeyError, IndexError):
            mac = ""

        if not mac: self.moduleShell.log.error("Unable to retrieve switch MAC address.")
        return 'mac_address.switch=' + mac

    ## Get the info from the Vitesse Ethernet Switch
    #
    #  @return: (version,config_version)
    #  @type: tuple(str, str)
    def getSwitchInfo(self):
        # In case we can't get the info, "not found." will be logged
        firmwareInfo = "Not found."
        configInfo = "Not found."
        try:
            # Open connection with the switch
            vtss = Vtss(switchIP=self.switchAddress)
            # Get the info from the switch
            # Get the firmware version
            jsonResp = vtss.callMethod(['firmware.status.switch.get'])
            # If no error, update the info
            if jsonResp['error'] == None:
                firmwareInfo = jsonResp['result'][0]['val']['Version']
            # Get the config info
            response = vtss.downloadFile('startup-config').splitlines()
            for version in reversed(response):
                # Version number should be the first line we find when we reverse the list
                # if we get empty strings, we should skip them
                if version == "":
                    continue
                # Is finds the "end" tag, not version found
                elif version == 'end':
                    break
                # this should be the version number
                else:
                    configInfo = version
                    break

        except Exception:
            self.moduleShell.log.error('Unable to retrieve the information from the switch.')

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
            minorVersion = str((i350firmware & 0xf00) >> 8)
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
        try:
            lines = check_output(['amidewrap' ,'/SS', '/SV']).splitlines()
        except (CalledProcessError, OSError):
            self.moduleShell.log.error('Unable to retrieve BIOS information.')
        else:
            for line in lines:
                if 'System version' in line:
                    line = line.split(" ")
                    biosInfo = line[-1]
                    break

        return 'version.BIOS='+biosInfo

    ## Private function
    #
    #  @param: offset
    def _readWord(self, offset):
        # Device
        if call(['ethtool', self.i350EthernetDev + '0'], stdout=DEVNULL, stderr=DEVNULL) != 0:
            self.moduleShell.log.error('Unable to acces i350 device %s',self.i350EthernetDev)
            return None
        else:
            # Call ethtool to read the word at the specified offset
            cmd = ['ethtool', '-e', self.i350EthernetDev + '0', 'offset', str(offset), 'length', '2', 'raw', 'on']
            ethtool = Popen(cmd, stdout=PIPE)
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
