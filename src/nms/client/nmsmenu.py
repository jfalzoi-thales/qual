import argparse
import os
from subprocess import call
from google.protobuf.message import Message

from tklabs_utils.classFinder.classFinder import ClassFinder
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


## Class that provides a menu-driven QTE simulator
class QTEMenu(object):
    ## Constructor
    # @param server  Host name or IP address of NMS
    # @param useGuest Connect to NMS Guest domain
    def __init__(self, server="localhost", useGuest=False):
        super(QTEMenu, self).__init__()

        ## ClassFinder for module ModuleMessages classes
        self.__modClass = ClassFinder(rootPaths=['nms.guest.modules'] if useGuest else ['nms.host.modules'],
                                     baseClass=ModuleMessages)
        ## ClassFinder for GPB message classes
        self.__qualMessage = ClassFinder(rootPaths=['nms.guest.pb2'] if useGuest else ['nms.host.pb2'],
                                         baseClass=Message)
        ## Exit flag
        self.__exit = False
        ## Guest or host
        self.useGuest = useGuest

        # Construct address to connect to
        address = str.format('tcp://{}:{}', server, 40006) if useGuest else "ipc:///tmp/nms.sock"

        prvKeyFile = ""
        pubServKeyFile = ""

        ## Client connection to NMS
        if os.path.isfile("/thales/host/config/zmq/MAP_hostsrv_zmq.pub") and useGuest:
            prvKeyFile = "/thales/host/appliances/nms/client/TKLabs_client_zmq.prv"
            pubServKeyFile = "/thales/host/config/zmq/MAP_hostsrv_zmq.pub"

            if not os.path.isfile("/thales/host/runtime/zmq-auth/NMS/TKLabs_client_zmq.key"):
                cmd = ["cp", "-f", "/thales/host/appliances/nms/client/TKLabs_client_zmq.pub", "/thales/host/runtime/zmq-auth/NMS/TKLabs_client_zmq.key"]

                if call(cmd) != 0:
                    print "Failed to Move Public Key File, Authentication Disabled"
                    prvKeyFile = ""
                    pubServKeyFile = ""

        self.client = ThalesZMQClient(address, timeout=7000, allowNoBody=True,
                                      prvKeyFile=prvKeyFile, pubServKeyFile=pubServKeyFile)

        print "Opened connection to", address
        print

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
            except KeyboardInterrupt:
                print
                self.__exit = True
                return

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
            print "Select an NMS %s Domain module:" % ("Guest" if self.useGuest else "Host")
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
            if self.__exit:
                return


## Main function for Qual menu test app
def main():
    # Parse command line arguments
    cmdParameters = argparse.ArgumentParser(description="Provides a menu-driven test interface to the NMS.")
    cmdParameters.add_argument('-s',
                               dest='server',
                               type=str,
                               default="localhost",
                               help="Host name or IP address of server")
    cmdParameters.add_argument('-g',
                               dest='useGuest',
                               action="store_true",
                               help="Connect to Guest domain NMS")
    args = cmdParameters.parse_args()

    # Initialize and run the QTE
    qte = QTEMenu(args.server, args.useGuest)
    qte.run()

    # Return exit code for qtemenu wrapper script
    return 0


if __name__ == "__main__":
    main()
