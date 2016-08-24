import argparse
from google.protobuf.message import Message

from tklabs_utils.classFinder.classFinder import ClassFinder
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.JsonZMQClient import JsonZMQClient
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


## Class that provides a menu-driven QTE simulator
class QTEMenu(object):
    ## Constructor
    # @param server  Host name or IP address of QTA
    # @param useJson Use JSON instead of GPB to communicate with QTA
    def __init__(self, server="localhost", useJson=False):
        super(QTEMenu, self).__init__()

        ## ClassFinder for module ModuleMessages classes
        self.__modClass = ClassFinder(rootPath='qual.modules',
                                     baseClass=ModuleMessages)
        ## ClassFinder for GPB message classes
        self.__qualMessage = ClassFinder(rootPath='qual.pb2',
                                         baseClass=Message)

        # Construct address to connect to
        address = str.format('tcp://{}:{}', server, 50002 if useJson else 50001)

        if useJson:
            ## Client connection to QTA
            self.client = JsonZMQClient(address, timeout=7000)
            print "Opened connection to", address, "for JSON messaging"
        else:
            ## Client connection to QTA
            self.client = ThalesZMQClient(address, timeout=7000)
            print "Opened connection to", address, "for GPB messaging"

    ## Print a menu of actions for a particular module
    def moduleMenu(self, modMsgClass):
        print ""
        while True:
            try:
                lastItem = 0
                print "Choose an action for", modMsgClass.getMenuTitle()
                for item in modMsgClass.getMenuItems():
                    print "\t%d - %s" % (lastItem, item[0])
                    lastItem += 1
                print "\t%d - Choose another module" % lastItem
                action = int(raw_input("Selection: "))
            except ValueError:
                print "Input must be a number."
                continue
            if action < 0 or action > lastItem:
                print "Valid range is 0 to %d." % lastItem
                continue
            print
            if action == lastItem:
                return

            msg = modMsgClass.getMenuItems()[action][1]()

            print "---------------------------------------------------------\n"
            print "Sending ", msg.__class__.__name__
            response = self.client.sendRequest(ThalesZMQMessage(msg))
            if (response.name == ""):
                print "No response\n"
            else:
                respClass = self.__qualMessage.getClassByName(response.name)
                if respClass is None:
                    print "Unexpected Value response\n"
                else:
                    respMsg = respClass()
                    respMsg.ParseFromString(response.serializedBody)
                    print "Received", respMsg.__class__.__name__
                    print respMsg
            print "---------------------------------------------------------\n"

    ## Print a list of modules and allow the user to select one
    def run(self):
        while True:
            index = 0
            msgClassList = []
            print "Select a module:"
            for msgClass in sorted(self.__modClass.classmap.values(), key=lambda e: e.getMenuTitle()):
                print "\t%d - %s" % (index, msgClass.getMenuTitle())
                msgClassList.append(msgClass)
                index += 1

            try:
                selectedModule = int(raw_input("Selection: "))
            except ValueError:
                print "Input must be a number."
                continue
            except KeyboardInterrupt:
                print
                return

            if selectedModule < 0 or selectedModule >= index:
                print "Valid range is %d to %d." % (0, index-1)
                continue
            self.moduleMenu(msgClassList[selectedModule])


if __name__ == "__main__":
    # Parse command line arguments
    cmdParameters = argparse.ArgumentParser(description="Provides a menu-driven test interface to the QTA.")
    cmdParameters.add_argument('-s',
                               dest='server',
                               type=str,
                               default="localhost",
                               help="Host name or IP address of server")
    cmdParameters.add_argument('-j',
                               dest='useJson',
                               action="store_true",
                               help="Use JSON format instead of GPB")
    args = cmdParameters.parse_args()

    # Initialize and run the QTE
    qte = QTEMenu(args.server, args.useJson)
    qte.run()
