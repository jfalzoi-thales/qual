import os
import socket
from subprocess import Popen, check_output, CalledProcessError, PIPE
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

        # Log firmware version information
        self.moduleShell.log.info("version.BIOS="           + self.getBiosInfo())
        self.moduleShell.log.info("version.i350_eeprom="    + self.geti350EepromVersion())
        self.moduleShell.log.info("version.i350_pxe="       + self.geti350PxeVersion())
        self.moduleShell.log.info("version.switch="         + self.getSwitchFirmwareVersion())
        self.moduleShell.log.info("version.switch_config="  + self.getSwitchConfigVersion())

        # Log MAC addresses
        self.moduleShell.log.info("mac_address.processor="  + self.getNicMac(self.cpuEthernetDev))
        self.moduleShell.log.info("mac_address.i350_1="     + self.getNicMac(self.i350EthernetDev + "0"))
        self.moduleShell.log.info("mac_address.i350_2="     + self.getNicMac(self.i350EthernetDev + "1"))
        self.moduleShell.log.info("mac_address.i350_3="     + self.getNicMac(self.i350EthernetDev + "2"))
        self.moduleShell.log.info("mac_address.i350_4="     + self.getNicMac(self.i350EthernetDev + "3"))
        self.moduleShell.log.info("mac_address.switch="     + self.getSwitchMac())

    ## Get local Ethernet MAC addresses
    #  @param   self
    #  @param   device      Device whose MAC address is being retrieved
    #  @return  MAC address string
    def getNicMac(self, device):
        try:
            mac = check_output(["cat", "/sys/class/net/%s/address" % device])
        except CalledProcessError:
            mac = ""

        if not mac: self.moduleShell.log.error("Unable to retrieve MAC address for device: %s" % device)
        return mac.rstrip()

    ## Get switch MAC address
    #  @param   self
    #  @return  MAC address string
    def getSwitchMac(self):
        try:
            vtss = Vtss(self.switchAddress)
            json = vtss.callMethod(["ip.status.interface.link.get"])
            mac = json["result"][0]["val"]["macAddress"]
        except (socket.error, KeyError, IndexError):
            mac = ""

        if not mac: self.moduleShell.log.error("Unable to retrieve switch MAC address.")
        return mac

    ## Get the switch firmware version
    #  @return: version info
    #  @type: str
    def getSwitchFirmwareVersion(self):
        # In case we can't get the info, "unknown" will be logged
        firmwareInfo = "unknown"

        try:
            # Open connection with the switch
            vtss = Vtss(switchIP=self.switchAddress)
            # Get the firmware version
            jsonResp = vtss.callMethod(['firmware.status.switch.get'])
            # If no error, look for something in the string that looks like a version number
            if jsonResp['error'] is None:
                for item in jsonResp['result'][0]['val']['Version'].split():
                    if item[0].isdigit():
                        firmwareInfo = item
                        break
        except Exception:
            self.moduleShell.log.error('Unable to retrieve the information from the switch.')

        return firmwareInfo

    ## Get the switch configuration version
    #  @return: version info
    #  @type: str
    def getSwitchConfigVersion(self):
        # In case we can't get the info, "unknown" will be logged
        configInfo = "unknown"

        try:
            # Open connection with the switch
            vtss = Vtss(switchIP=self.switchAddress)
            # Download the config file
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

        return configInfo

    ## Get the I350 EEPROM version
    #  @return: version info
    #  @type: str
    def geti350EepromVersion(self):
        # In case we can't get the info, "unknown" will be logged
        i350_eeprom = 'unknown'

        # Read version word from EEPROM
        eePromValue = self._readWord(0x0a)
        if eePromValue is not None:
            majorVersion = str((eePromValue & 0xf000) >> 12)
            minorVersion = str(eePromValue & 0xff)

            # OEM version number is in a different EEPROM word
            eePromValue = self._readWord(0x0c)
            if eePromValue is not None:
                oem = str(eePromValue)
                # If we reach this point, we have the major and the minor version, and the OEM
                # We can construct the complete version number
                i350_eeprom = '%s.%s.%s' % (majorVersion, minorVersion, oem)

        return i350_eeprom

    ## Get the I350 PXE Firmware version
    #  @return: version info
    #  @type: str
    def geti350PxeVersion(self):
        # In case we can't get the info, "unknown" will be logged
        i350_pxe = 'unknown'

        # Read PXE Firmware version word from EEPROM
        eePromValue = self._readWord(0x64)
        if eePromValue is not None:
            majorVersion = str((eePromValue & 0xf000) >> 12)
            minorVersion = str((eePromValue & 0xf00) >> 8)
            buildNumber = str(eePromValue & 0xff)
            # If we reach this point, we have the major and the minor version, and the OEM
            # We can construct the complete version number
            i350_pxe = '%s.%s.%s' % (majorVersion, minorVersion, buildNumber)

        return i350_pxe

    ## Get BIOS version
    #  @return: version info
    #  @type: str
    def getBiosInfo(self):
        # In case we can't get the info, "unknown" will be logged
        biosInfo = 'unknown'
        # get information
        try:
            lines = check_output(['amidewrap' ,'/SS', '/SV']).splitlines()
        except (CalledProcessError, OSError):
            self.moduleShell.log.error('Unable to retrieve BIOS information.')
        else:
            for line in lines:
                if 'System version' in line:
                    line = line.split(" ")
                    biosInfo = line[-1].strip('"')
                    break

        return biosInfo

    ## Private function - read word from I350 EEPROM
    #
    #  @param: offset
    def _readWord(self, offset):
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
