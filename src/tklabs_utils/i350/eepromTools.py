import os
import subprocess

from tklabs_utils.configurableObject.configurableObject import ConfigurableObject


## Discard the output
DEVNULL = open(os.devnull, 'wb')


## I350 EEPROM tools Class
class EepromTools(ConfigurableObject):
    ## Constructor
    #  @param   self
    #  @param   log  Log object for this object to use
    def __init__(self, log):
        # Initialize parent class
        super(EepromTools, self).__init__(configSection="CarrierCardInventory")

        ## Log object
        self.log = log
        ## Name of I350 Ethernet device
        self.i350EthernetDev = "ens1f"
        ## Magic code for ethtool to write to EEPROM - hardware-dependent
        self.ethtoolMagic = "0x15238086"
        # Load configuration from config file
        self.loadConfig(attributes=("i350EthernetDev", "ethtoolMagic"))
        ## Ethernet device for I350
        self.ethDevice = self.i350EthernetDev + '0'

    ## Reads VPD from EEPROM
    #  @param  self
    #  @return VPD data
    def readVPD(self):
        # We store the 256-byte VPD block at offset 0x3e00
        self.log.debug("Reading VPD block from EEPROM")
        cmd = ['ethtool', '-e', self.ethDevice, 'offset', '0x3e00', 'length', '256', 'raw', 'on']
        self.log.debug("Reading from command: %s" % " ".join(cmd))
        ethtool = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        vpd = ethtool.stdout.read(256)
        rc = ethtool.wait()
        self.log.debug("ethtool command returned: %d" % rc)
        if rc != 0:
            vpd = None
        return vpd

    ## Writes VPD block to EEPROM
    #  @param  self
    #  @param  vpd  Encoded VPD data
    #  @return True if write was successful, False if not
    def writeVPD(self, vpd):
        # We store the 256-byte VPD block at offset 0x3e00
        self.log.info("Writing VPD block to EEPROM")
        cmd = ['ethtool', '-E', self.ethDevice, 'magic', self.ethtoolMagic, 'offset', '0x3e00']
        self.log.debug("Writing %d bytes to command: %s" % (len(vpd), " ".join(cmd)))
        ethtool = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        ethtool.stdin.write(vpd)
        ethtool.stdin.close()
        rc = ethtool.wait()
        self.log.debug("ethtool command returned: %d" % rc)
        return rc == 0

    ## Writes VPD pointer to EEPROM
    #  @param  self
    #  @return True if write was successful, False if not
    def writeVPDPointer(self):
        # I350 stores a pointer to the VPD block at offset 0x5e
        # First read to see if the value is already set correctly
        self.log.debug("Reading VPD pointer value from EEPROM")
        ptr = self.readWord(0x5e)
        if ptr is None:
            self.log.error("Unable to read VPD pointer from EEPROM")
            return False

        # Pointer is in words, so our byte offset of 0x3e00 is word offset of 0x1f00
        if ptr == 0x1f00:
            self.log.debug("VPD pointer is already set correctly")
            return True

        # Wasn't set correctly, so let's set it
        self.log.info("Writing VPD pointer value to EEPROM")
        return self.writeWord(0x5e, 0x1f00)

    ## Reads a 2-byte word from EEPROM
    #  @param  self
    #  @param  offset  offset (in bytes)
    #  @return None if read was unsuccessful, otherwise integer value that was read
    def readWord(self, offset):
        # Call ethtool to read the word at the specified offset
        cmd = ['ethtool', '-e', self.ethDevice, 'offset', str(offset), 'length', '2', 'raw', 'on']
        self.log.debug("Reading from command: %s" % " ".join(cmd))
        ethtool = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        data = ethtool.stdout.read(2)
        rc = ethtool.wait()
        self.log.debug("ethtool command returned: %d" % rc)
        if rc != 0:
            return None

        # Values are stored little-endian
        val =  (ord(data[1]) << 8) | ord(data[0])
        self.log.debug("Read value 0x%x", val)
        return val

    ## Writes a 2-byte word to EEPROM
    #  @param  self
    #  @param  offset  offset (in bytes)
    #  @param  val     value to write
    #  @return True if successful, False if not
    def writeWord(self, offset, val):
        # Values are stored little-endian
        data = bytearray()
        data.append(val & 0xff)
        data.append((val >> 8) & 0xff)

        # Call ethtool to write the word at the specified offset
        cmd = ['ethtool', '-E', self.ethDevice, 'magic', self.ethtoolMagic, 'offset', str(offset)]
        self.log.debug("Writing 2 bytes to command: %s" % " ".join(cmd))
        ethtool = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        ethtool.stdin.write(data)
        ethtool.stdin.close()
        rc = ethtool.wait()
        self.log.debug("ethtool command returned: %d" % rc)
        return rc == 0

    ## Enables LAN Boot (PXE) in EEPROM
    #  @param  self
    #  @return True if successful, False if not
    def enableLanBoot(self):
        try:
            rc = subprocess.call(["bootutil64e", "-all", "-fe"], stdout=DEVNULL)
        except OSError:
            rc = -1
        return rc == 0
