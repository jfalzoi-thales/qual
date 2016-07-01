
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

        ## Ethernet device for i350
        self.ethDevice = "TEST_FILE"
        #self.ethDevice = "enp2s0f0"
        ## Enable WRITE_PROTECT function
        self.enableWriteProtect = False
        # Load configuration from config file
        self.loadConfig(attributes=("ethDevice", "enableWriteProtect"))

        if self.ethDevice == "TEST_FILE":
            # Create our test file
            self.log.info("Simulating EEPROM using local file vpd.bin")
            vpd = bytearray()
            for i in range(0, 256):
                vpd.append(0xff)
            self.writeVPD(vpd)
        else:
            # Make sure we can talk to the device
            rc = subprocess.call(['ethtool', self.ethDevice], stdout=DEVNULL, stderr=DEVNULL)
            if rc != 0:
                raise CarrierCardDataModuleException(msg="Unable to access device %s" % self.ethDevice)

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
        vpd = self.readVPD()
        if vpd is None:
            self.log.error("Failure reading VPD")
            response.error.error_code = ErrorMsg.FAILURE_READ_FAILED
            response.error.description = "Read VPD from EEPROM failed"
        elif ord(vpd[0]) == 0x82:
            self.parseVPD(vpd)
            for key, value in self.vpdEntries.items():
                kv = response.values.add()
                kv.key = self.vpdToHDDS[key]
                kv.value = value
            response.success = True
            # TODO: Populate response.writeProtected field
        else:
            self.log.debug("No VPD read; returning empty list")
            response.success = True

    ## Handles requests with requestType of WRITE
    #  @param    self
    #  @param    request     Message body with request details
    #  @param    response    CarrierCardDataResponse object
    def handleWrite(self, request, response):
        # Validate supplied entries
        for kv in request.values:
            if kv.key not in self.hddsToVPD:
                response.success = False
                response.error.error_code = ErrorMsg.FAILURE_INVALID_KEY
                response.error.description = "Invalid key: %s" % kv.key
                return
            elif len(kv.value) == 0 or len(kv.value) > self.lengthLimits[kv.key]:
                response.success = False
                response.error.error_code = ErrorMsg.FAILURE_INVALID_VALUE
                response.error.description = "Invalid value for key: %s" % kv.key
                return

        # Start by reading existing VPD, to which we'll add supplied values
        vpd = self.readVPD()
        if vpd is not None and ord(vpd[0]) == 0x82:
            self.parseVPD(vpd)
        else:
            self.vpdEntries.clear()

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
        else:
            # Write the VPD pointer into EEPROM if necessary
            response.success = self.writeVPDPointer()
            if not response.success:
                self.log.error("Failure writing VPD pointer")
                response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
                response.error.description = "Write VPD pointer to EEPROM failed"
            else:
                # Return all current entries in response
                for key, value in self.vpdEntries.items():
                    kv = response.values.add()
                    kv.key = self.vpdToHDDS[key]
                    kv.value = value

    ## Handles requests with requestType of ERASE
    #  @param    self
    #  @param    response    CarrierCardDataResponse object
    def handleErase(self, response):
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
            response.success = False
            response.error.error_code = ErrorMsg.FAILURE_WRITE_PROTECT_DISABLED
            response.error.description = "Write Protect function disabled"
        else:
            # TODO: Implement write protect
            # TODO: If no data has been written, disallow write protect
            self.log.error("Write protect not implemented")
            response.success = False
            response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
            response.error.description = "Write Protect failed"

    ## Read VPD from EEPROM, or simulate doing so
    #  @param  self
    #  @return VPD data
    def readVPD(self):
        vpd = None
        if self.ethDevice == "TEST_FILE":
            self.log.debug("Reading from file vpd.bin")
            try:
                fh = open("vpd.bin", "rb")
                vpd = fh.read(256)
                fh.close()
            except IOError:
                self.log.error("Unable to read vpd.bin file")
            if len(vpd) <= 1:
                self.log.error("Short read from vpd.bin file")
                vpd = None
        else:
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

    ## Write VPD block to EEPROM, or simulate doing so
    #  @param  self
    #  @param  vpd  Encoded VPD data
    #  @return True if write was successful, False if not
    def writeVPD(self, vpd):
        rc = 0
        if self.ethDevice == "TEST_FILE":
            self.log.debug("Writing %d bytes to file vpd.bin" % len(vpd))
            fh = open("vpd.bin", "wb")
            fh.write(str(vpd))
            fh.close()
        else:
            self.log.info("Writing VPD block to EEPROM")
            cmd = ['ethtool', '-E', self.ethDevice, 'magic', '0x15218086', 'offset', '0x3e00']
            self.log.debug("Writing %d bytes to command: %s" % (len(vpd), " ".join(cmd)))
            ethtool = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            ethtool.stdin.write(vpd)
            ethtool.stdin.close()
            rc = ethtool.wait()
            self.log.debug("ethtool command returned: %d" % rc)
        return rc == 0

    ## Write VPD pointer to EEPROM
    #  @param  self
    #  @return True if write was successful, False if not
    def writeVPDPointer(self):
        if self.ethDevice == "TEST_FILE":
            # nothing to do
            self.log.debug("Real Ethernet device would check and update VPD pointer field")
            return True

        # i350 stores the a pointer to the VPD block at offset 0x5E
        # First read to see if the value is already set correctly
        self.log.debug("Reading VPD pointer value from EEPROM")
        cmd = ['ethtool', '-e', self.ethDevice, 'offset', '0x5E', 'length', '2', 'raw', 'on']
        self.log.debug("Reading from command: %s" % " ".join(cmd))
        ethtool = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        ptr = ethtool.stdout.read(2)
        rc = ethtool.wait()
        self.log.debug("ethtool command returned: %d" % rc)
        if rc != 0:
            return False

        # Pointer is in words, so our byte offset of 0x3e00 is word offset of 0x1f00
        if ord(ptr[0]) == 0 and ord(ptr[1]) == 0x1f:
            self.log.debug("VPD pointer is already set correctly")
            return True

        # Wasn't set correctly, so let's set it
        self.log.info("Writing VPD pointer value to EEPROM (value was 0x%02x%02x)" % (ord(ptr[1]), ord(ptr[0])))
        cmd = ['ethtool', '-E', self.ethDevice, 'magic', '0x15218086', 'offset', '0x5E']
        self.log.debug("Writing 2 bytes to command: %s" % " ".join(cmd))
        ethtool = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        ethtool.stdin.write(b"\x00\x1f")
        ethtool.stdin.close()
        rc = ethtool.wait()
        self.log.debug("ethtool command returned: %d" % rc)
        return rc == 0

    ## Parse VPD data and store parsed values in self.vpdEntries
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

    ## Parse VPD inner block and store parsed values in self.vpdEntries
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

    ## Build VPD data from values in self.vpdEntries
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
