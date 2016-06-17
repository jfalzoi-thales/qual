import inspect
import os
import sys

from ConfigParser import SafeConfigParser, NoOptionError
from common.configurableObject.exception import ConfigurableObjectException
from common.configurableObject.platform import PLATFORM
from common.logger.logger import Logger


## A class loads configuration files from INI.
#
class ConfigurableObject(object):

    def __init__(self, iniFile=None):

        ## Logger implementation, based on standard python logger
        self.log = Logger(type(self).__name__)

        self.__iniFile = iniFile
        if self.__iniFile is None:
            moduleDir = os.path.dirname(inspect.getsourcefile(self.__class__))
            while os.path.basename(moduleDir) != 'src':
                moduleDir = os.path.dirname(moduleDir)
            self.__iniFile = moduleDir + os.path.sep + 'qual' + os.path.sep + 'config' + os.path.sep + PLATFORM + '.ini'

        self.__iniParser = SafeConfigParser()
        self.__iniParser.read(self.__iniFile)


        return

    def loadConfig(self, attributes=(), sectionName = None):

        if sectionName is None:
            sectionName = type(self).__name__

        for attribute in attributes :

            if self.__iniParser.has_option(sectionName, attribute) :
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
                setattr(self, attribute, handler(sectionName, attribute))
            except NoOptionError:
                pass

        return

