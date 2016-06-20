import inspect
import os
import sys


from ConfigParser import SafeConfigParser, NoOptionError
from common.configurableObject.exception import ConfigurableObjectException
from common.logger.logger import Logger


## A class loads configuration files from INI.
#
class ConfigurableObject(object):

    def __init__(self, configSection=None):

        ## Logger implementation, based on standard python logger
        self.log = Logger(type(self).__name__)
        self.__iniFile = None
        self.__iniPath = self._findConfig()
        self.__iniParser = SafeConfigParser()
        self.__iniParser.read(self.__iniPath)
        self.__iniSection = configSection if configSection is not None else type(self).__name__

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


    def _findConfig(self):
        #
        # Search for the INI file.
        # For each of the following 3, look in the CWD first, then the config folder second. (Total 6 checks)
        # 1) If this is running as a unit test, look for a unitTest.ini first
        # 2) Then look for platform.ini, which should be present on the target
        # 3) Then look for virtualMachine, which should always be present for testing

        iniCandidates = ['platform', 'virtualMachine']
        if 'unittest' in sys.modules:
            iniCandidates.insert(0, 'unitTest')
        for iniFile in iniCandidates:

            #First, look in the local directory
            if os.path.isfile('%s.ini' % (iniFile)):
                self.__iniFile = iniFile
                return '%s.ini' % (iniFile)

            #If its not there, look in the config directory
            moduleDir = os.path.dirname(inspect.getsourcefile(self.__class__))
            while os.path.basename(moduleDir) != 'src':
                moduleDir = os.path.dirname(moduleDir)
            moduleDir = moduleDir + os.path.sep + 'qual' + os.path.sep + 'config'
            if not os.path.isdir(moduleDir):
                raise ConfigurableObjectException('Could not find configuration directory %s' % (moduleDir,))
            filepath = moduleDir + os.path.sep + iniFile + '.ini'
            if os.path.isfile(filepath):
                self.__iniFile = iniFile
                return filepath

        raise ConfigurableObjectException('INI File not found')


    def loadConfig(self, attributes=()):

        for attribute in attributes :
            if self.__iniParser.has_option(self.__iniSection, attribute) :
                try:
                    current = getattr(self, attribute)
                except AttributeError:
                    current = 'stringValue'
                if isinstance(current, bool) :
                    handler = self.__iniParser.getboolean
                elif isinstance(current, int) :
                    handler = self.__iniParser.getint
                elif isinstance(current, float) :
                    handler = self.__iniParser.getfloat
                elif isinstance(current, str) :
                    handler = self.__iniParser.get
                else:
                    raise ConfigurableObjectException('Could not configure Field %s, unsupported Type' % (attribute,))
            else:
                self.log.info('Setting configuration value %s without default' % (attribute,))
                handler = self.__iniParser.get

            try:
                setattr(self, attribute, handler(self.__iniSection, attribute))
            except NoOptionError:
                pass

        return

