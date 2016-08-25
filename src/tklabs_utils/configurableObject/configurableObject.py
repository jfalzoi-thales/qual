import inspect
import os
import sys
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

from tklabs_utils.configurableObject.exception import ConfigurableObjectException


## A class loads configuration files from INI.
class ConfigurableObject(object):

    if 'unittest' in sys.modules:
        _iniFileList = ['unitTest','sims',]
    else:
        _iniFileList = ['sims',]

    @classmethod
    def setIniFilename(cls, filename):
        cls._iniFileList.insert(0, filename)


    ##Constructor
    # @param self
    # @param configSection INI File section to read configuration from (default to class name)
    def __init__(self, configSection=None):
        # Init the superclass
        super(ConfigurableObject, self).__init__()
        self._iniFile = None
        self._iniPath = self._findConfig()
        self._iniParser = SafeConfigParser()
        self._iniParser.read(self._iniPath)
        self._iniSection = configSection if configSection is not None else type(self).__name__

        return

    ## Class Method for returning configurations
    #
    # This function returns the INI sections that will be used to instantiate the modules.
    # By default, 1 instance of the module will be created, and will be initialized using
    # a sections that matches the classname of the module (e.g. Ethernet).
    #
    # If this method is overridden, a different sections name could be used, or if multiple
    # section names are listed then mulitple instances of the module will be created, one
    # for each section name
    #
    # Example:
    #   for config in Example.getConfigurations():
    #    example = Example(config=config)
    #
    #
    # @param cls Class, passed to classMethod
    #
    @classmethod
    def getConfigurations(cls):
        return [cls.__name__, ]

    ## Load class attributes/member variables from INI files
    #
    # This function accepts a list of member variable names that will be
    # overridden by values in an INI file.  The File location and Section name
    # are determined in the constructor.  Each variable name will be set by a value
    # of the same type as the current value.
    #
    #@param attributes A List of member variable names (strings) to be set by INI values
    def loadConfig(self, attributes):

        for attribute in attributes:
            #
            # So there is a "behavior" in the configParser that in order for the "DEFAULT" section to be read,
            # The target section has to exist.  This causes a problem since the DEFAULT should be in effect even
            # If the target section is totally missing (IMO), so lets explicitly check both.
            if self._iniParser.has_option(self._iniSection, attribute) or self._iniParser.has_option('DEFAULT', attribute):
                try:
                    current = getattr(self, attribute)
                except AttributeError:
                    current = 'stringValue'

                if isinstance(current, bool):
                    handler = self._iniParser.getboolean
                elif isinstance(current, int):
                    handler = self._iniParser.getint
                elif isinstance(current, float):
                    handler = self._iniParser.getfloat
                elif isinstance(current, str):
                    handler = self._iniParser.get
                else:
                    raise ConfigurableObjectException(
                        'Could not configure Field %s, unsupported Type' % (attribute,))

                try:
                    try:
                        setattr(self, attribute, handler(self._iniSection, attribute))
                    except NoSectionError:
                        setattr(self, attribute, handler('DEFAULT', attribute))
                except (NoOptionError,NoSectionError):
                    pass

            else:
                try:
                    self.log.debug('Config %s not in INI %s:%s ' % (attribute,self._iniFile,self._iniSection))
                except AttributeError:
                    #The object may not have a log setup yet, and configurableObject
                    #can't have a log itself because logger is a configurableObject.
                    pass


        return


    def _findConfig(self):
        #
        # Search for the INI file.
        # For each of the following 3, look in the CWD first, then the config folder second. (Total 6 checks)
        # 1) If this is running as a unit test, look for a unitTest.ini first
        # 2) Then look for platform.ini, which should be present on the target
        # 3) Then look for sims.ini, which should always be present for testing
        for iniFile in ConfigurableObject._iniFileList:

            #First, look in the local directory
            if os.path.isfile('%s.ini' % (iniFile)):
                self._iniFile = iniFile
                return '%s.ini' % (iniFile)

            #If its not there, look in the config directory
            moduleDir = os.path.dirname(inspect.getsourcefile(self.__class__))
            if 'src' in moduleDir:
                while os.path.basename(moduleDir) != 'src':
                    moduleDir = os.path.dirname(moduleDir)
                moduleDir = os.path.join(moduleDir,'config')
            else:
                # Try relative to the current directory
                moduleDir = os.path.join('config')

            if not os.path.isdir(moduleDir):
                raise ConfigurableObjectException('Could not find configuration directory %s' % (moduleDir,))
            filepath = os.path.join(moduleDir, '%s.ini' % (iniFile,))
            if os.path.isfile(filepath):
                self._iniFile = iniFile
                return filepath

        raise ConfigurableObjectException('INI File not found: %s ' % (ConfigurableObject._iniFileList))

