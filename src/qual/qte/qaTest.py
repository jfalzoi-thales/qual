import argparse
import unittest
from google.protobuf.message import Message

from tklabs_utils.classFinder.classFinder import ClassFinder
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.tzmq.JsonZMQClient import JsonZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


## Class that provides a menu-driven QTE simulator
class QATest(object):
    ## Constructor
    # @param server  Host name or IP address of QTA
    # @param listModules Use JSON instead of GPB to communicate with QTA
    def __init__(self, server="localhost", testMod=None):
        super(QATest, self).__init__()
        ConfigurableObject.setFilename("qual")

        ## ClassFinder for module unit test classes
        self.__modClass = ClassFinder(rootPaths=['qual.modules'],
                                     baseClass=unittest.TestCase)

        if testMod is not None and "Test_" + testMod not in self.__modClass.classmap:
            print "Module test '%s' not found." % testMod
            testMod = None

        if testMod is None:
            print
            print "Available module tests:"
            index = 1
            modList = []
            for mod in sorted(self.__modClass.classmap):
                print "\t%d - %s" % (index, mod.replace("Test_", ""))
                modList.append(mod)
                index += 1
            while testMod is None:
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
                testMod = modList[selectedModule - 1]

        ## ClassFinder for GPB message classes
        self.__qualMessage = ClassFinder(rootPaths=['qual.pb2'],
                                         baseClass=Message)

        # Construct address to connect to - use JSON port
        address = str.format('tcp://{}:{}', server, 50002)

        ## Client connection to QTA
        self.client = JsonZMQClient(address, timeout=7000)
        print "Opened connection to", address, "for JSON messaging"

        # Run class unit test suite
        testClass = self.__modClass.classmap["Test_" + testMod]
        testClass.module = self
        suite = unittest.TestLoader().loadTestsFromTestCase(testClass)
        unittest.TextTestRunner(verbosity=1).run(suite)

    ## Send a message to the QTA and return response
    def msgHandler(self, msg):
        response = self.client.sendRequest(msg)
        # Deserialize response
        if response.name == "":
            print "No response"
        else:
            respClass = self.__qualMessage.getClassByName(response.name)
            if respClass is None:
                print "Unexpected Value response"
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
    cmdParameters.add_argument('module',
                               nargs='*',
                               help="Module to test; if not present a list of modules will be displayed")
    args = cmdParameters.parse_args()

    # Initialize and run the Qual/ATP Tester
    testMod = args.module[0] if len(args.module) > 0 else None
    QATest(args.server, testMod)

    # Return exit code for qatest wrapper script
    # TODO: Return unittest status
    return 0


if __name__ == "__main__":
    main()
