import argparse
import sys
import unittest
from google.protobuf.message import Message

from tklabs_utils.classFinder.classFinder import ClassFinder
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.tzmq.JsonZMQClient import JsonZMQClient


## Class that provides a menu-driven QTE simulator
class QATest(object):
    ## Constructor
    # @param server  Host name or IP address of QTA
    # @param listModules Use JSON instead of GPB to communicate with QTA
    def __init__(self, server, moduleNames):
        super(QATest, self).__init__()
        ConfigurableObject.setFilename("qual")

        ## ClassFinder for module unit test classes
        self.moduleFinder = ClassFinder(rootPaths=['qual.modules'],
                                        baseClass=unittest.TestCase)

        ## ClassFinder for GPB message classes
        self.messageFinder = ClassFinder(rootPaths=['qual.pb2', 'common.pb2'],
                                         baseClass=Message)

        # "Unsafe" tests - exclude from "all" list
        unsafeTests = ["Test_SSDErase", "Test_MacAddress"]

        # Extract any parameters
        params = {}
        for arg in moduleNames:
            if '=' in arg:
                splitArg = arg.split('=')
                if len(splitArg) > 1:
                    params[splitArg[0]] = splitArg[1]

        # Build list of module test classes to run
        testClasses = []
        testPattern = ""
        if "sanity" in moduleNames:
            print "Sanity check tests requested."
            for testClassName, testClass in self.moduleFinder.classmap.items():
                if testClassName in unsafeTests or "FirmwareUpdate" in testClassName:
                    print "Skipping unsafe test '%s'" % testClassName.replace("Test_", "")
                else:
                    testClasses.append(testClass)
        else:
            for moduleName in moduleNames:
                if '=' in moduleName:
                    continue
                if "Test_" + moduleName in self.moduleFinder.classmap:
                    testClasses.append(self.moduleFinder.classmap["Test_" + moduleName])
                else:
                    print "Module test '%s' not found." % moduleName
                    testPattern = moduleName

        # If no valid module name specified on command line, print a menu
        if len(testClasses) == 0:
            print
            index = 1
            modList = []
            if testPattern:
                patternMatches = [mod for mod in sorted(self.moduleFinder.classmap) if testPattern in mod]
                if patternMatches:
                    print "Available module tests matching '%s':" % testPattern
                    for mod in patternMatches:
                        print "\t%d - %s" % (index, mod.replace("Test_", ""))
                        modList.append(mod)
                        index += 1
            if not modList:
                print "Available module tests:"
                for mod in sorted(self.moduleFinder.classmap):
                    print "\t%d - %s" % (index, mod.replace("Test_", ""))
                    modList.append(mod)
                    index += 1
            while len(testClasses) == 0:
                try:
                    selectedModule = int(raw_input("Test to run: "))
                except ValueError:
                    print "Input must be a number."
                    continue
                except KeyboardInterrupt:
                    print
                    return
                if selectedModule < 1 or selectedModule > index:
                    print "Valid range is %d to %d." % (1, index)
                    continue
                testClasses.append(self.moduleFinder.classmap[modList[selectedModule - 1]])

        # Construct address to connect to - use JSON port
        address = str.format('tcp://{}:{}', server, 50002)

        ## Client connection to QTA
        self.client = JsonZMQClient(address, timeout=20000)
        print "Opened connection to", address, "for JSON messaging"

        # Build a test suite of all requested module tests
        suite = unittest.TestSuite()
        for testClass in testClasses:
            testClass.module = self
            testClass.params = params
            suite.addTest(unittest.TestLoader().loadTestsFromTestCase(testClass))

        # Run class unit test suite
        print "----------------------------------------------------------------------"
        sys.stdout.flush()
        unittest.TextTestRunner(verbosity=1).run(suite)

    ## Send a message to the QTA and return response
    def msgHandler(self, msg):
        # Update timeout for FirmwareUpdateRequest
        if msg.__class__.__name__ == 'FirmwareUpdateRequest':
            timeout = 480000
        else:
            timeout = 20000
        # Send the request
        response = self.client.sendRequest(msg, timeout=timeout)
        # Deserialize response if necessary
        if response.name == "":
            print "No response to %s" % msg.name
            sys.stdout.flush()
        elif response.body is None:
            respClass = self.messageFinder.getClassByName(response.name)
            if respClass is None:
                print "Unexpected message type %s in response to %s" % (response.name, msg.name)
            else:
                respMsg = respClass()
                respMsg.ParseFromString(response.serializedBody)
                response.body = respMsg
        return response

    ## Dummy terminate method since some unit tests will try to access it
    def terminate(self):
        pass

## Main function for Qual/ATP Tester app
def main():
    # Parse command line arguments
    cmdParameters = argparse.ArgumentParser(description="Provides a CLI interface to run Qual/ATP tests.")
    cmdParameters.add_argument('-s',
                               dest='server',
                               type=str,
                               default="localhost",
                               help="Host name or IP address of server")
    cmdParameters.add_argument('modules',
                               nargs='*',
                               help="Modules to test; if not present a list of modules will be displayed")
    args = cmdParameters.parse_args()

    # Initialize and run the Qual/ATP Tester
    QATest(args.server, args.modules)

    # Return exit code for qatest wrapper script
    # TODO: Return unittest status
    return 0


if __name__ == "__main__":
    main()
