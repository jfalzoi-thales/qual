import inspect
import os
import pkgutil
import sys


class ClassFinder(object):

    def __init__(self, rootPath, baseClass):
        self.messageMap = {}
        __import__(rootPath)
        package = sys.modules[rootPath]
        if package != None:

            packagePath = os.path.dirname(package.__file__)
            modules = [name for _, name, _ in pkgutil.iter_modules([packagePath])]
            for module in modules:
                moduleImport = rootPath + '.' + module
                try:
                    __import__(moduleImport)
                except Exception as e:
                    print moduleImport, 'Import error', e
                    continue

                for name, obj in inspect.getmembers(sys.modules[moduleImport]):
                    if inspect.isclass(obj):
                        if isinstance(obj, baseClass):
                            self.messageMap[name] = obj

    def getClassByName(self, name):
        if name in self.messageMap.keys() :
            return self.messageMap[name]
        else:
            return None


