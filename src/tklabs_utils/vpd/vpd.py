## VPD Parser/builder Class
class VPD(object):
    ## Constructor
    #  @param   self
    #  @param   log       Logger object to use for logging
    #  @param   validKeys List of valid keys
    def __init__(self, log, validKeys):
        # Initialize parent class
        super(VPD, self).__init__()

        ## Logger
        self.log = log
        ## Allowed keys
        self.validKeys = validKeys
        ## VPD entries
        self.vpdEntries = {}

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
            elif key in self.validKeys:
                self.log.debug("VPD parser found %s = \"%s\"" % (key, value))
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
