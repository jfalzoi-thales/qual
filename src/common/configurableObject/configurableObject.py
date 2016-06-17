import copy
import inspect
import os
import sys
import threading

from ConfigParser import SafeConfigParser
from common.configurableObject.platform import PLATFORM



## A class loads configuration files from INI.
#
from common.logger.logger import Logger


class ConfigurableObject(object):
    __sem = threading.Semaphore()
    __iniParser = None

    platform = PLATFORM
    configFile = None
    unitTestExecution = 'unittest' in sys.modules

    @classmethod
    def __readFile(cls):
        ## Back up to the src directory, then go into config
        moduleDir = os.path.dirname(inspect.getsourcefile(cls))
        while os.path.basename(moduleDir) != 'src':
            moduleDir = os.path.dirname(moduleDir)
        cls.configFile = moduleDir + os.path.sep + 'qual'+ os.path.sep + 'config'+ os.path.sep + cls.platform + '.ini'

        cls.__iniParser = SafeConfigParser()
        cls.__iniParser.read(cls.configFile)


        return

    def __init__(self, sectionName = None):
        ConfigurableObject.__sem.acquire()
        if ConfigurableObject.__iniParser is None:
            ConfigurableObject.__readFile()
        ConfigurableObject.__sem.release()

        if sectionName is None:
            sectionName = self.__class__.__name__
        self.sectionName = sectionName

        self.log = Logger('config_%s' % (self.sectionName))


        return

    def loadConfig(self, defaults={}):

        retVal = copy.deepcopy(defaults)
        parser = ConfigurableObject.__iniParser

        if self.sectionName not in parser.sections():
            self.log.warning('Section %s not found in %s' % (self.sectionName, ConfigurableObject.configFile))
            return retVal

        for field, value in parser.items(self.sectionName) :
            if field not in retVal.keys() :
                self.log.debug('undefined key %s set to %s' % (field, value))
                retVal[field] = value
            else :
                if isinstance(retVal[field], int) :
                    retVal[field] = parser.getint(self.sectionName, field)
                elif isinstance(retVal[field], float) :
                    retVal[field] = parser.getfloat(self.sectionName, field)
                elif isinstance(retVal[field], bool) :
                    retVal[field] = parser.getboolean(self.sectionName, field)
                else:
                    retVal[field] = value
                self.log.debug('defined key %s set to %s' % (field, value))

        print 'YIP'
        return retVal


