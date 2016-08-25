import argparse
from threading import Thread
from time import sleep
from google.protobuf.message import Message

from tklabs_utils.classFinder.classFinder import ClassFinder
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.JsonZMQClient import JsonZMQClient
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


## Class that gives the QTA a good hammering by sending many simultaneous messages
class QTEHammer(object):
    ## Constructor
    # @param server  Host name or IP address of QTA
    # @param useJson Use JSON instead of GPB to communicate with QTA
    def __init__(self, server="localhost", useJson=False):
        super(QTEHammer, self).__init__()

        ## Logger implementation, based on standard python logger
        self.log = Logger(type(self).__name__)
        ## ClassFinder for module ModuleMessages classes
        self.__modClass = ClassFinder(rootPath='qual.modules',
                                     baseClass=ModuleMessages)
        ## ClassFinder for GPB message classes
        self.__qualMessage = ClassFinder(rootPath='qual.pb2',
                                         baseClass=Message)
        ## List for storing threads
        self.threads = []
        ## List for storing ZMQ clients
        self.clients = []
        ## List for storing types of messages
        self.msgClassList = []
        ## Threads exit when self.quit = True
        self.quit = False
        ## Store JSON flag for client use
        self.useJson = useJson
        ## Address to connect to
        self.address = str.format('tcp://{}:{}', server, 50002 if useJson else 50001)

    ## Thread for hammering individual module
    #  @param   self
    #  @param   index  Index of client, thread, and msgClassList
    def hammerTime(self, index):
        self.sendTypes(("Connect", "Run"), index)
        sleep(2)

        while not self.quit:
            self.sendTypes(("Get", "Report", "Read"), index)
            sleep(2)

        self.sendTypes(("Disconnect", "Stop"), index)

    ## Sends specified message types to QTA
    #  @param   self
    #  @param   msgs    Types of messages to send
    #  @param   index   Index of client, thread, and msgClassList
    def sendTypes(self, msgs, index):
        #  For each type of message for current, module, find all message types that start with msgs and send them
        for types in self.msgClassList[index].getMenuItems():
            if types[0].startswith(msgs):
                msg = types[1]()
                self.log.info("Sending %s of type %s" % (msg.__class__.__name__, types[0]))
                response = self.clients[index].sendRequest(ThalesZMQMessage(msg))

                #  Check that we received the proper response from the QTA
                if (response.name == ""):
                    self.log.warning("No response from QTA for %s" % msg.__class__.__name__)
                else:
                    respClass = self.__qualMessage.getClassByName(response.name)

                    if respClass is None:
                        self.log.warning("Unexpected Value response from %s" % msg.__class__.__name__)
                    else:
                        respMsg = respClass()
                        respMsg.ParseFromString(response.serializedBody)
                        self.log.info("Received %s %s" % (respMsg.__class__.__name__, respMsg))

    ## Stores message types and starts threads for each module
    #  @param   self
    def run(self):
        index = 0

        for msgClass in sorted(self.__modClass.classmap.values(), key=lambda e: e.getMenuTitle()):
            #  Modules can be excluded by adding their 'MenuTitle' to the list
            if msgClass.getMenuTitle() not in ["Carrier Card Data"]:
                self.msgClassList.append(msgClass)
                self.log.info("Starting thread for %s." % self.msgClassList[index].getMenuTitle())
                self.threads.append(Thread(target=self.hammerTime, args=(index,)))

                if self.useJson:
                    ## Client connection to QTA
                    self.clients.append(JsonZMQClient(self.address, timeout=2000))
                    self.log.info("Opened connection to %s for JSON messaging" % self.address)
                else:
                    ## Client connection to QTA
                    self.clients.append(ThalesZMQClient(self.address, timeout=2000))
                    self.log.info("Opened connection to %s for GPB messaging" % self.address)

                self.threads[index].start()
                sleep(1)
                index += 1

        sleep(30)
        self.quit = True

if __name__ == "__main__":
    # Parse command line arguments
    cmdParameters = argparse.ArgumentParser(description="Gives the QTA a good hammering.")
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

    # Initialize and run the qteHammer
    qteHammer = QTEHammer(args.server, args.useJson)
    qteHammer.run()