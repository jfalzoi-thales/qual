import time
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.classFinder.classFinder import ClassFinder
from common.module.modulemsgs import ModuleMessages
from google.protobuf.message import Message

# @cond doxygen_unittest

## QTARequestManager
#  Manage different type request to QTA Application
class QTARequestManager(ThalesZMQClient):
    def __init__(self):
        super(QTARequestManager, self).__init__("tcp://localhost:50001")
        self.__modClass = ClassFinder(rootPath='qual.modules',
                                     baseClass=ModuleMessages)
        self.__qualMessage = ClassFinder(rootPath='common.gpb.python',
                                     baseClass=Message)

    def runTest(self, modMsgClass):
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
            response = self.sendRequest(ThalesZMQMessage(msg))
            respClass = self.__qualMessage.getClassByName(response.name)
            if respClass is None:
                print "Unexpected Value response"
            else:
                respMsg = respClass()
                respMsg.ParseFromString(response.serializedBody)
                print "Received", respMsg.__class__.__name__
                print respMsg
                print "---------------------------------------------------------\n"

    def runManager(self):
        while True:
            index = 0
            msgClassList = []
            print "Select a module:"
            for msgClass in self.__modClass.classmap.values():
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
            self.runTest(msgClassList[selectedModule])


if __name__ == "__main__":
    man = QTARequestManager()
    man.runManager()

## @endcond
