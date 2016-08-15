
import os
import subprocess
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.CarrierCardData_pb2 import CarrierCardDataRequest, CarrierCardDataResponse, ErrorMsg
from common.module.module import Module, ModuleException


## Discard the output
DEVNULL = open(os.devnull, 'wb')


## CarrierCardData Module Exception Class
class CarrierCardDataModuleException(ModuleException):
    ## Constructor
    #  @param     self
    #  @param     msg  Message text associated with this exception
    def __init__(self, msg):
        super(CarrierCardDataModuleException, self).__init__()
        ## Message text associated with this exception
        self.msg = msg


## CarrierCardData Module Class
class CarrierCardData(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        # Initialize parent class
        super(CarrierCardData, self).__init__(config)

        ## Ethernet device for I350
        self.ethDevice = "TEST_FILE"
        ## Magic code for ethtool to write to EEPROM - hardware-dependent
        self.ethtoolMagic = "0x15238086"
        ## Enable WRITE_PROTECT function
        self.enableWriteProtect = False
        # Load configuration from config file
        self.loadConfig(attributes=("ethDevice", "enableWriteProtect", "ethtoolMagic"))

        if self.enableWriteProtect:
            self.log.info("Write protect function enabled")

        if self.ethDevice == "TEST_FILE":
            # Create our VPD test file
            self.log.info("Simulating EEPROM using local file /tmp/vpd.bin")
            vpd = bytearray()
            for i in range(0, 256):
                vpd.append(0xff)
            self.writeVPD(vpd)
            # Also create test files for the other words we read/write
            self.writeWord(0x5e, 0xffff)
            self.writeWord(0x24, 0x5c80)
        else:
            # Make sure we can talk to the device
            rc = subprocess.call(['ethtool', self.ethDevice], stdout=DEVNULL, stderr=DEVNULL)
            if rc != 0:
                raise CarrierCardDataModuleException(msg="Unable to access device %s" % self.ethDevice)
            self.log.info("Using Ethernet device %s", self.ethDevice)

        ## Map two-character VPD field names to HDDS field names
        self.vpdToHDDS = {"PN": "part_number",
                          "SN": "serial_number",
                          "EC": "revision",
                          "VP": "manufacturer_pn",
                          "VD": "manufacturing_date",
                          "VN": "manufacturer_name",
                          "VC": "manufacturer_cage"}

        ## Map HDDS field names to two-character VPD field names
        self.hddsToVPD = {v: k for k, v in self.vpdToHDDS.items()}

        ## Length limits, indexed by HDDS key
        self.lengthLimits = self.hddsToVPD.copy()
        for key in self.lengthLimits:
            self.lengthLimits[key] = 8 if key in ("revision", "manufacturing_date", "manufacturer_cage") else 24

        ## VPD entries
        self.vpdEntries = {}

        # Add handler to available message handlers
        self.addMsgHandler(CarrierCardDataRequest, self.handleMsg)

    ## Handles incoming CarrierCardDataRequest messages
    #
    #  Receives TZMQ request and performs requested action
    #  @param     self
    #  @param     msg       TZMQ format message
    #  @return    a ThalesZMQMessage object containing the response message
    def handleMsg(self, msg):
        response = CarrierCardDataResponse()

        if msg.body.requestType == CarrierCardDataRequest.READ:
            self.handleRead(response)
        elif msg.body.requestType == CarrierCardDataRequest.WRITE:
            self.handleWrite(msg.body, response)
        elif msg.body.requestType == CarrierCardDataRequest.ERASE:
            self.handleErase(response)
        elif msg.body.requestType == CarrierCardDataRequest.WRITE_PROTECT:
            self.handleWriteProtect(response)
        else:
            self.log.error("Unexpected Request Type %d" % msg.body.requestType)
            response.success = False
            response.error.error_code = ErrorMsg.FAILURE_INVALID_MESSAGE
            response.error.description = "Invalid Request Type"

        return ThalesZMQMessage(response)

    ## Handles requests with requestType of READ
    #  @param    self
    #  @param    response    CarrierCardDataResponse object
    def handleRead(self, response):
        success = self.readAndParseVPD()
        if not success:
            self.log.error("Failure reading VPD")
            response.error.error_code = ErrorMsg.FAILURE_READ_FAILED
            response.error.description = "Read VPD from EEPROM failed"
            return

        response.success = True
        response.writeProtected = self.getWriteProtectFlag()
        for key, value in self.vpdEntries.items():
            kv = response.values.add()
            kv.key = self.vpdToHDDS[key]
            kv.value = value

    ## Handles requests with requestType of WRITE
    #  @param    self
    #  @param    request     Message body with request details
    #  @param    response    CarrierCardDataResponse object
    def handleWrite(self, request, response):
        # Check if write-protected
        response.writeProtected = self.getWriteProtectFlag()
        if response.writeProtected:
            self.log.warning("Attempt to write to write-protected EEPROM")
            response.success = False
            response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
            response.error.description = "Cannot write: EEPROM is write-protected"
            return

        # Validate supplied entries
        for kv in request.values:
            if kv.key not in self.hddsToVPD:
                self.log.warning("Attempt to write invalid key %s" % kv.key)
                response.success = False
                response.error.error_code = ErrorMsg.FAILURE_INVALID_KEY
                response.error.description = "Invalid key: %s" % kv.key
                return
            elif len(kv.value) == 0 or len(kv.value) > self.lengthLimits[kv.key]:
                self.log.warning("Attempt to write invalid value for key %s" % kv.key)
                response.success = False
                response.error.error_code = ErrorMsg.FAILURE_INVALID_VALUE
                response.error.description = "Invalid value for key: %s" % kv.key
                return

        # Start by reading existing VPD, to which we'll add supplied values
        self.readAndParseVPD()

        # Update self.vpdEntries with new entries from request
        for kv in request.values:
            vpdKey = self.hddsToVPD[kv.key]
            self.log.debug("Updating %s (%s) = \"%s\"" % (vpdKey, kv.key, kv.value))
            self.vpdEntries[vpdKey] = kv.value

        # Build the updated VPD and write to EEPROM
        response.success = self.writeVPD(self.buildVPD())
        if not response.success:
            self.log.error("Failure writing VPD block")
            response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
            response.error.description = "Write VPD block to EEPROM failed"
            return

        # Write the VPD pointer into EEPROM if necessary
        response.success = self.writeVPDPointer()
        if not response.success:
            self.log.error("Failure writing VPD pointer")
            response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
            response.error.description = "Write VPD pointer to EEPROM failed"
            return

        # Return all current entries in response
        for key, value in self.vpdEntries.items():
            kv = response.values.add()
            kv.key = self.vpdToHDDS[key]
            kv.value = value

    ## Handles requests with requestType of ERASE
    #  @param    self
    #  @param    response    CarrierCardDataResponse object
    def handleErase(self, response):
        # Check if write-protected
        response.writeProtected = self.getWriteProtectFlag()
        if response.writeProtected:
            self.log.warning("Attempt to erase write-protected EEPROM")
            response.success = False
            response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
            response.error.description = "Cannot erase: EEPROM is write-protected"
            return

        # Write VPD area with all 0xff bytes
        vpd = bytearray()
        for i in range(0, 256):
            vpd.append(0xff)
        response.success = self.writeVPD(vpd)
        if not response.success:
            self.log.error("Failure writing VPD block")
            response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
            response.error.description = "Write VPD block to EEPROM failed"

    ## Handles requests with requestType of WRITE_PROTECT
    #  @param    self
    #  @param    response    CarrierCardDataResponse object
    def handleWriteProtect(self, response):
        if not self.enableWriteProtect:
            self.log.warning("Attempt to write-protect when WP function is disabled")
            response.success = False
            response.error.error_code = ErrorMsg.FAILURE_WRITE_PROTECT_DISABLED
            response.error.description = "Write Protect function disabled"
            return

        # Check if already write-protected
        response.writeProtected = self.getWriteProtectFlag()
        if response.writeProtected:
            self.log.info("Attempt to write-protect already write-protected EEPROM")
            # It's already in the state the user requested, so we'll consider this a success
            response.success = True
            return

        # Sanity check: make sure that there is data programmed before we write-protect
        self.readAndParseVPD()
        # Arbitrary: check for programmed part number and serial number
        if "PN" not in self.vpdEntries or "SN" not in self.vpdEntries:
            self.log.warning("Attempt to write-protect when required data is missing")
            response.success = False
            response.error.error_code = ErrorMsg.FAILURE_INVALID_VALUE
            response.error.description = "Write protect request refused: VPD not yet programmed"
            return

        # Go ahead and attempt to set the write-protect flag.  No turning back now!
        response.success = self.setWriteProtectFlag()
        if not response.success:
            self.log.error("Error setting write protect flag")
            response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
            response.error.description = "Write Protect failed"
            return

        # Successful, so now we can set the writeProtected flag in the response
        response.writeProtected = True
        self.log.info("**** EEPROM is now write-protected ****")

    ## Reads VPD from EEPROM (or test file) and updates self.vpdEntries
    #  @param  self
    #  @return True on successful read, False on failure
    def readAndParseVPD(self):
        vpd = self.readVPD()
        if vpd is None:
            self.vpdEntries.clear()
            return False
        if ord(vpd[0]) == 0x82:
            self.parseVPD(vpd)
        else:
            self.log.debug("VPD area not programmed")
            self.vpdEntries.clear()
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
            self.log.info("Writing VPD block to file /tmp/vpd.bin")
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

    ## Parses VPD data and stores parsed values in self.vpdEntries
    #  @param  self
    #  @param  vpd  encoded VPD data
    def parseVPD(self, vpd):
        # Delete any previous VPD entries
        self.vpdEntries.clear()

        self.log.debug("Parsing VPD")

        # First byte must be 0x82
        if ord(vpd[0]) != 0x82:
            self.log.debug("VPD parser attempted to parse from non-VPD buffer")
            return

        # Parse the identifier.  We don't actually use this.
        pos = 3 + ord(vpd[1])
        identifier = vpd[3:pos]
        self.log.debug("VPD parser found Identifier = \"%s\"" % identifier)

        # Loop through VPD blocks.  There are 3 defined tags: Read-only data,
        # Read-write data, and End.  Data tags are followed by a two-byte
        # (little-endian) size, and <size> data bytes, broken into fields.
        done = False
        while not done:
            if pos >= 256:
                # Our VPD block can contain at most 256 bytes, so stop parsing at that point
                self.log.warning("VPD parser reached max size without seeing end tag")
                done = True
            elif ord(vpd[pos]) == 0x78:
                self.log.debug("VPD parser found End tag")
                done = True
            elif ord(vpd[pos]) == 0x90:
                self.log.debug("VPD parser found Read-only block")
                pos += 1
                blockLen = ord(vpd[pos])
                pos += 2
                # This parses the fields in the block and stores them in self.vpdEntries
                self.parseVPDBlock(vpd[pos:pos + blockLen])
                pos += blockLen
            elif ord(vpd[pos]) == 0x91:
                self.log.debug("VPD parser found Read-write block (ignoring)")
                pos += 1
                blockLen = ord(vpd[pos])
                pos += 2
                # We don't use the read-write block, so just skip it.
                pos += blockLen
            else:
                self.log.warning("VPD parser found unknown block tag 0x%x" % ord(vpd[pos]))
                done = True

    ## Parses VPD inner block and stores parsed values in self.vpdEntries
    #  @param  self
    #  @param  block  encoded VPD block
    def parseVPDBlock(self, block):
        pos = 0
        while pos < len(block):
            key = block[pos:pos + 2]
            pos += 2
            dataLen = ord(block[pos])
            pos += 1
            value = block[pos:pos + dataLen]
            pos += dataLen
            if key == "RV":
                self.log.debug("VPD parser found Block checksum = 0x%x" % ord(value[0]))
            elif key in self.vpdToHDDS:
                hddsKey = self.vpdToHDDS[key]
                self.log.debug("VPD parser found %s (%s) = \"%s\"" % (key, hddsKey, value))
                self.vpdEntries[key] = value
            else:
                self.log.warning("VPD parser found unknown %s = \"%s\"" % (key, value))
                # Ignore unknown keys, other than logging a warning

    ## Builds VPD data from values in self.vpdEntries
    #  @param  self
    #  @return encoded VPD data
    def buildVPD(self):
        identifier = "MPS Carrier Card"
        vpd = bytearray()
        vpd.append(0x82)             # Identifier tag
        vpd.append(len(identifier))  # Length of identifier - low byte
        vpd.append(0)                # Length of identifier - high byte
        vpd.extend(identifier)       # Identifier
        vpd.append(0x90)             # Read-only section tag
        roLenPos = len(vpd)          # Save the position where the length byte will go
        vpd.extend((0, 0))           # Placeholder for read-only section length
        roDataStart = len(vpd)       # Save the start of the read-only data

        # Append the fields from self.vpdEntries
        self.log.debug("VPD builder adding %d entries to read-only block" % len(self.vpdEntries))
        for key, value in self.vpdEntries.items():
            vpd.extend(str(key))
            vpd.append(len(value))
            vpd.extend(str(value))

        # Save the end of the read-only data, allowing for the checksum field
        roDataEnd = len(vpd)
        roDataEnd += 4

        # Fill in the length of the read-only data field
        vpd[roLenPos] = roDataEnd - roDataStart

        # Add the checksum field
        vpd.extend("RV")
        vpd.append(1)
        checksum = 0
        for byte in vpd:
            checksum = (checksum + byte) % 256
        vpd.append((256 - checksum) % 256)

        # Add the end tag
        vpd.append(0x78)

        # Pad to 256 bytes
        self.log.debug("VPD builder data length = %d, padding to 256" % len(vpd))
        while len(vpd) < 256:
            vpd.append(0xff)

        return vpd

    ## Cleans up test files
    #  @param     self
    def terminate(self):
        if self.ethDevice == "TEST_FILE":
            os.remove("/tmp/vpd.bin")
            os.remove("/tmp/word24.bin")
            os.remove("/tmp/word5e.bin")
