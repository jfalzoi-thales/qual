import os
import subprocess
from ConfigParser import SafeConfigParser


## SEMA Inventory Class
class SEMAInventory(object):
    ## Constructor
    #  @param   self
    #  @param   log  Log object for this object to use
    def __init__(self, log):
        # Initialize parent class
        super(SEMAInventory, self).__init__()

        ## Log object
        self.log = log
        ## Compressed file to access
        self.compressedFile = "/thales/host/runtime/SEMADrv/flash"
        ## Temporary uncompressed file to work on
        self.uncompressedFile = "/tmp/SEMAflash.work"

    ## Read values in the inventory area
    #  @param    self
    #  @param    values     dict of values indexed by HDDS key
    def read(self, values):
        # Read values from file
        configParser = SafeConfigParser()
        if os.path.exists(self.compressedFile):
            if subprocess.call("gunzip -c %s > %s" % (self.compressedFile, self.uncompressedFile), shell=True) == 0:
                configParser.read(self.uncompressedFile)

                for section in configParser.sections():
                    for option in configParser.options(section):
                        hddsKey = "inventory.%s.%s" % (section, option)
                        values[hddsKey] = configParser.get(section, option)

    ## Update values in the inventory area
    #  @param    self
    #  @param    values     dict of values to update
    #  @return   True if success, False if failure
    def update(self, values):
        # Start by reading existing values, to which we'll add supplied values
        configParser = SafeConfigParser()
        if os.path.exists(self.compressedFile):
            if subprocess.call("gunzip -c %s > %s" % (self.compressedFile, self.uncompressedFile), shell=True) == 0:
                configParser.read(self.uncompressedFile)

        # Update configParser with new entries from request
        for key, value in values.items():
            # Key has form inventory.<section>.<item>
            splitKey = key.split('.')
            section = splitKey[1]
            item = splitKey[2]
            if not configParser.has_section(section):
                configParser.add_section(section)
            self.log.debug("Updating %s.%s = \"%s\"" % (section, item, value))
            configParser.set(section, item, value)

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
        if subprocess.call("gzip -c %s > %s" % (self.uncompressedFile, self.compressedFile), shell=True) != 0:
            self.log.error("Unable to write compressed inventory data")
            return False

        # Successful
        return True
