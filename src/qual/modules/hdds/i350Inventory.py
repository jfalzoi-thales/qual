import os
import subprocess

from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.vpd.vpd import VPD


## Discard the output
DEVNULL = open(os.devnull, 'wb')


## I350 Inventory Class
class I350Inventory(ConfigurableObject):
    ## Constructor
    #  @param   self
    #  @param   log  Log object for this object to use
    def __init__(self, log):
        # Initialize parent class
        super(I350Inventory, self).__init__(configSection="CarrierCardInventory")

        ## Log object
        self.log = log
        ## Name of I350 Ethernet device
        self.i350EthernetDev = "ens1f"
        ## Magic code for ethtool to write to EEPROM - hardware-dependent
        self.ethtoolMagic = "0x15238086"
        ## Enable WRITE_PROTECT function
        self.enableWriteProtect = False
        # Load configuration from config file
        self.loadConfig(attributes=("i350EthernetDev", "enableWriteProtect", "ethtoolMagic"))

        if self.enableWriteProtect:
            self.log.info("Write protect function enabled")

        ## Ethernet device for I350
        self.ethDevice = self.i350EthernetDev + '0'
        # Make sure we can talk to the device
        if subprocess.call(['ethtool', self.ethDevice], stdout=DEVNULL, stderr=DEVNULL) == 0:
            self.log.info("Using Ethernet device %s", self.ethDevice)
        else:
            self.log.warning("Unable to access I350 device %s for carrier card inventory" % self.ethDevice)
            self.log.warning("Simulating I350 EEPROM using local file /tmp/vpd.bin")
            self.ethDevice = "TEST_FILE"
            # Create our VPD test file
            vpd = bytearray()
            for i in range(0, 256):
                vpd.append(0xff)
            self.writeVPD(vpd)
            # Also create test files for the other words we read/write
            self.writeWord(0x5e, 0xffff)
            self.writeWord(0x24, 0x5c80)

        ## Map two-character VPD field names to HDDS field names
        self.vpdToHDDS = {"PN": "inventory.carrier_card.part_number",
                          "SN": "inventory.carrier_card.serial_number",
                          "EC": "inventory.carrier_card.revision",
                          "VP": "inventory.carrier_card.manufacturer_pn",
                          "VD": "inventory.carrier_card.manufacturing_date",
                          "VN": "inventory.carrier_card.manufacturer_name",
                          "VC": "inventory.carrier_card.manufacturer_cage"}

        ## Map HDDS field names to two-character VPD field names
        self.hddsToVPD = {v: k for k, v in self.vpdToHDDS.items()}

        ## VPD parser/builder
        self.vpd = VPD(self.log, self.vpdToHDDS.keys())

    ## Read and parse the inventory area and return all values
    #  @param    self
    #  @param    values  dict of values indexed by HDDS key or None if read error occurred
    def read(self, values):
        success = self.readAndParseVPD()
        if not success:
            self.log.error("Failure reading VPD data")
            return None

        # Build a new dict indexed by HDDS key instead of VPD key
        values = {}
        for key, value in self.vpd.vpdEntries.items():
            hddsKey = self.vpdToHDDS[key]
            values[hddsKey] = value

    ## Update values in the inventory area
    #  @param    self
    #  @param    values     dict of values to update
    #  @return   True if success, False if failure
    def update(self, values):
        # Check if write-protected
        if self.getWriteProtectFlag():
            self.log.warning("Attempt to write to write-protected EEPROM")
            return False

        # Start by reading existing VPD, to which we'll add supplied values
        self.readAndParseVPD()

        # Update self.vpdEntries with new entries from request
        for key, value in values.items():
            if key in self.hddsToVPD:
                vpdKey = self.hddsToVPD[key]
                self.log.debug("Updating %s (%s) = \"%s\"" % (vpdKey, key, value))
                self.vpd.vpdEntries[vpdKey] = value
            else:
                self.log.warning("Attempted to write invalid key: %s" % key)
                return False

        # Build the updated VPD and write to EEPROM
        success = self.writeVPD(self.vpd.buildVPD())
        if not success:
            self.log.error("Failure writing VPD block")
            return False

        # Write the VPD pointer into EEPROM if necessary
        success = self.writeVPDPointer()
        if not success:
            self.log.error("Failure writing VPD pointer")
            return False

        # Successful
        return True

    ## Erase the inventory area
    #  @param    self
    #  @return   True if success, False if failure
    def erase(self):
        # Check if write-protected
        if self.getWriteProtectFlag():
            self.log.warning("Attempt to erase write-protected EEPROM")
            return False

        # Write VPD area with all 0xff bytes
        vpd = bytearray()
        for i in range(0, 256):
            vpd.append(0xff)
        success = self.writeVPD(vpd)
        if not success:
            self.log.error("Failure writing VPD block")
            return False

        # Successful
        return True

    ## Write-protect the inventory area
    #  @param    self
    #  @return   tuple of success, error message
    def writeProtect(self):
        if not self.enableWriteProtect:
            self.log.warning("Attempt to write-protect when WP function is disabled")
            return False

        # Check if already write-protected
        if self.getWriteProtectFlag():
            self.log.info("Attempt to write-protect already write-protected EEPROM")
            # It's already in the state the user requested, so we'll consider this a success
            return True

        # Sanity check: make sure that there is data programmed before we write-protect
        self.readAndParseVPD()
        # Arbitrary: check for programmed part number and serial number
        if "PN" not in self.vpd.vpdEntries or "SN" not in self.vpd.vpdEntries:
            self.log.warning("Attempt to write-protect when required data is missing")
            return False

        # Go ahead and attempt to set the write-protect flag.  No turning back now!
        success = self.setWriteProtectFlag()
        if not success:
            self.log.error("Error setting write protect flag")
            return False

        # Successful
        self.log.info("**** EEPROM is now write-protected ****")
        return True

    ## Reads VPD from EEPROM (or test file) and updates self.vpdEntries
    #  @param  self
    #  @return True on successful read, False on failure
    def readAndParseVPD(self):
        vpd = self.readVPD()
        if vpd is None:
            self.vpd.vpdEntries.clear()
            return False
        if ord(vpd[0]) == 0x82:
            self.vpd.parseVPD(vpd)
        else:
            self.log.debug("VPD area not programmed")
            self.vpd.vpdEntries.clear()
        return True

    ## Reads VPD from EEPROM (or test file)
    #  @param  self
    #  @return VPD data
    def readVPD(self):
        vpd = None
        if self.ethDevice == "TEST_FILE":
            self.log.debug("Reading from file /tmp/vpd.bin")
            try:
                fh = open("/tmp/vpd.bin", "rb")
                vpd = fh.read(256)
                fh.close()
            except IOError:
                self.log.error("Unable to read /tmp/vpd.bin file")
            if len(vpd) <= 1:
                self.log.error("Short read from /tmp/vpd.bin file")
                vpd = None
        else:
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

    ## Writes VPD block to EEPROM (or test file)
    #  @param  self
    #  @param  vpd  Encoded VPD data
    #  @return True if write was successful, False if not
    def writeVPD(self, vpd):
        if self.ethDevice == "TEST_FILE":
            self.log.debug("Writing VPD block to file /tmp/vpd.bin")
            fh = open("/tmp/vpd.bin", "wb")
            fh.write(str(vpd))
            fh.close()
            return True

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

    ## Reads write-protect flag from EEPROM (or test file)
    #  @param  self
    #  @return True if EEPROM is write-protected, False if not
    def getWriteProtectFlag(self):
        # I350 stores the write-protect flag in a word at offset 0x24
        self.log.debug("Reading protection word from EEPROM")
        word = self.readWord(0x24)
        if word is None:
            # Don't know, so assume not write-protected
            return False
        # Bit 4 is the protection bit
        return (word & 0x10) != 0

    ## Sets write-protect flag in EEPROM (or test file)
    #  @param  self
    #  @return True if set was successful, False if not
    def setWriteProtectFlag(self):
        # I350 stores the write-protect flag in a word at offset 0x24
        self.log.debug("Reading protection word from EEPROM")
        word = self.readWord(0x24)
        if word is None:
            self.log.error("Unable to read protection word from EEPROM")
            return False

        # Top two bits are signature and must be 01; check this before writing
        if (word >> 14) != 1:
            self.log.error("Protection word 0x%x doesn't have correct signature" % word)
            return False

        # Bit 4 is the protection bit
        word |= 0x10
        self.log.info("Writing protection word to EEPROM")
        return self.writeWord(0x24, word)

    ## If in test file mode, resets the protection mode to the default (unprotected) state
    #
    #  Used for unit testing.
    #  @param  self
    def resetProtectionTestFile(self):
        if self.ethDevice == "TEST_FILE":
            self.writeWord(0x24, 0x5c80)

    ## Reads a 2-byte word from EEPROM (or test file)
    #  @param  self
    #  @param  offset  offset (in bytes)
    #  @return None if read was unsuccessful, otherwise integer value that was read
    def readWord(self, offset):
        if self.ethDevice == "TEST_FILE":
            # Read word from test file
            testfile = "/tmp/word%x.bin" % offset
            self.log.debug("Reading from file %s" % testfile)
            try:
                fh = open(testfile, "rb")
                data = fh.read(2)
                fh.close()
            except IOError:
                self.log.error("Unable to read word.bin file")
                return None
            if len(data) < 2:
                self.log.error("Short read from word.bin file")
                return None
        else:
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

    ## Writes a 2-byte word to EEPROM (or test file)
    #  @param  self
    #  @param  offset  offset (in bytes)
    #  @param  val     value to write
    #  @return True if successful, False if not
    def writeWord(self, offset, val):
        # Values are stored little-endian
        data = bytearray()
        data.append(val & 0xff)
        data.append((val >> 8) & 0xff)

        if self.ethDevice == "TEST_FILE":
            # Write word to test file
            testfile = "/tmp/word%x.bin" % offset
            self.log.debug("Writing 0x%x to file %s" % (val, testfile))
            fh = open(testfile, "wb")
            fh.write(str(data))
            fh.close()
            return True
        else:
            # Call ethtool to write the word at the specified offset
            cmd = ['ethtool', '-E', self.ethDevice, 'magic', self.ethtoolMagic, 'offset', str(offset)]
            self.log.debug("Writing 2 bytes to command: %s" % " ".join(cmd))
            ethtool = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            ethtool.stdin.write(data)
            ethtool.stdin.close()
            rc = ethtool.wait()
            self.log.debug("ethtool command returned: %d" % rc)
            return rc == 0


    ## Cleans up test files
    #  @param     self
    def cleanup(self):
        if self.ethDevice == "TEST_FILE":
            os.remove("/tmp/vpd.bin")
            os.remove("/tmp/word24.bin")
            os.remove("/tmp/word5e.bin")
