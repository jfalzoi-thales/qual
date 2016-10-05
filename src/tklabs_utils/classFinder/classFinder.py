import inspect
import os
import pkgutil
import sys

## A class that searches a tree for instances of a class, and allows lookup by class name
class ClassFinder(object):

    ##Constructor
    #@param rootPaths : The root paths to start searching for instances of baseClass
    #@param baseClass : The baseClass whose derivations we are collecting
    def __init__(self, rootPaths, baseClass):
        ##Map of classes to class names
        self.classmap = {}
        self.searchInPackage(rootPaths, baseClass)

    ## Recursively search a tree for instances of a class
    # @param rootPaths : The root paths to start searching for instances of baseClass
    # @param baseClass : The baseClass whose derivations we are collecting
    def searchInPackage(self, rootPaths, baseClass):
        for rootPath in rootPaths:
            __import__(rootPath)
            package = sys.modules[rootPath]
            if package != None:

                packagePath = os.path.dirname(package.__file__)
                modules = [(name, isPackage) for i, name, isPackage in pkgutil.iter_modules([packagePath])]

                for module in modules:
                    if module[1]:
                        self.searchInPackage(['%s.%s' % (rootPath, module[0])],baseClass)
                    else:
                        moduleImport = rootPath + '.' + module[0]
                        try:
                            __import__(moduleImport)
                        except Exception as e:
                            print moduleImport, 'Import error', e
                            continue

                        for name, obj in inspect.getmembers(sys.modules[moduleImport]):
                            if inspect.isclass(obj):
                                if baseClass in obj.__bases__:
                                    self.classmap[name] = obj

    ##Returns a class by name, or None if unknown
    def getClassByName(self, name):
        if name in self.classmap.keys() :
            return self.classmap[name]
        else:
            return None


