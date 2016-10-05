import os
from subprocess import call, check_output, CalledProcessError
from ConfigParser import SafeConfigParser


## IFE Inventory Class
class IFEInventory(object):
    ## Constructor
    #  @param   self
    #  @param   log  Log object for this object to use
    def __init__(self, log):
        # Initialize parent class
        super(IFEInventory, self).__init__()

        ## Log object
        self.log = log
        ## Compressed file to write and program into EEPROM
        self.compressedFile = "/tmp/IFEInventory.gz"
        ## Temporary uncompressed file to work on
        self.uncompressedFile = "/tmp/IFEInventory.work"

    ## Read values in the IFE inventory file
    #  @param    self
    #  @param    values     dict of values indexed by HDDS key
    def read(self, values):
        self.readEEPROM()
        # Read values from file
        configParser = SafeConfigParser()
        if os.path.exists(self.compressedFile):
            # gunzip returns 0 on success, 1 on failure, 2 on warning - running on MPS can return warning which is OK
            if call("gunzip -c %s > %s" % (self.compressedFile, self.uncompressedFile), shell=True) != 1:
                configParser.read(self.uncompressedFile)

                for section in configParser.sections():
                    for option in configParser.options(section):
                        hddsKey = "inventory.%s.%s" % (section, option)
                        values[hddsKey] = configParser.get(section, option)

    ## Update values in the IFE inventory file
    #  @param    self
    #  @param    values     dict of values to update
    #  @return   True if success, False if failure
    def update(self, values):
        # Start by reading existing values, to which we'll add supplied values
        configParser = SafeConfigParser()
        if os.path.exists(self.compressedFile):
            # gunzip returns 0 on success, 1 on failure, 2 on warning - running on MPS can return warning which is OK
            if call("gunzip -c %s > %s" % (self.compressedFile, self.uncompressedFile), shell=True) != 1:
                configParser.read(self.uncompressedFile)

        # Update configParser with new entries from request
        for key, value in values.items():
            # Key has form inventory.<section>.<item>
            splitKey = key.split('.')
            if len(splitKey) == 3:
                section = splitKey[1]
                item = splitKey[2]
                if not configParser.has_section(section):
                    configParser.add_section(section)
                self.log.debug("Updating %s.%s = \"%s\"" % (section, item, value))
                configParser.set(section, item, value)
            else:
                self.log.warning("Attempted to write invalid key: %s" % key)
                return False

        # Write the file
        if os.path.exists(self.uncompressedFile):
            os.remove(self.uncompressedFile)
        try:
            with open(self.uncompressedFile, 'wb') as configFile:
                configParser.write(configFile)
        except IOError:
            self.log.error("Unable to write inventory data")
            return False

        # Create the compressed file
        if call("gzip -c %s > %s" % (self.uncompressedFile, self.compressedFile), shell=True) != 0:
            self.log.error("Unable to write compressed inventory data")
            return False

        return self.writeEEPROM()

    ## Reads EEPROM area data into IFE inventory file
    #  @param    self
    def readEEPROM(self):
        endCnt = 0
        addr = 0x00
        bytes = bytearray()

        while True:
            try:
                byte = int(check_output(["eeprom", hex(addr)]).rstrip(), 16)
            except CalledProcessError:
                self.log.error("Unable to read inventory data from EEPROM")
                byte = 0xFF

            addr += 0x01

            if byte == 0xFF:
                endCnt += 1
            else:
                bytes.append(byte)

            if endCnt == 4: break

        if bytes:
            if os.path.exists(self.compressedFile):
                os.remove(self.compressedFile)
            try:
                with open(self.compressedFile, 'wb') as inventoryFile:
                    inventoryFile.write(str(bytes))
            except IOError:
                self.log.error("Unable to write EEPROM inventory data to file")
        else:
            self.log.error("Empty data from EEPROM")

    ## Writes IFE inventory file to EEPROM area
    #  @param    self
    #  @return   True if success, False if failure
    def writeEEPROM(self):
        addr = 0x00

        try:
            with open(self.compressedFile, 'rb') as inventoryFile:
                data = inventoryFile.read()
        except IOError:
            self.log.error("Unable to read EEPROM inventory data from file")
            return False

        bytes = bytearray(data)

        for byte in bytes:
            call(["eeprom", hex(addr), hex(byte)])
            addr += 0x01

        for i in range(0, 4):
            call(["eeprom", hex(addr), "0xFF"])
            addr += 0x01

        return True
