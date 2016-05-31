import time
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.classFinder.classFinder import ClassFinder
from common.module.module import Module
from google.protobuf.message import Message

## QTARequestManager
#  Manage different type request to QTA Application
class QTARequestManager(ThalesZMQClient):
    def __init__(self):
        super(QTARequestManager, self).__init__("tcp://localhost:50001")
        self.__modClass = ClassFinder(rootPath='qual.modules',
                                     baseClass=Module)
        self.__qualMessage = ClassFinder(rootPath='common.gpb.python',
                                     baseClass=Message)

    def runTest(self, msgClassName):
        msgClass = self.__qualMessage.getClassByName(msgClassName)
        msg = msgClass()
        print ""
        while True:
            try:
                time.sleep(0.5)
                print ("Choose an action:\n\t0 - Stop\n\t1 - Run\n\t2 - Report\n\t3 - Choose another module")
                action = int(raw_input("Selection: "))
            except ValueError:
                print "Input must be a number."
                continue
            if action < 0 or action > 3:
                print "Valid range is 0 to 3."
                continue
            print
            if action == 0:
                msg.requestType = msgClass.STOP
            elif action == 1:
                msg.requestType = msgClass.RUN
            elif action == 2:
                msg.requestType = msgClass.REPORT
            else:
                return

            print "---------------------------------------------------------\n"
            print "Sending ", msg.__class__.__name__
            response = self.sendRequest(ThalesZMQMessage(msg))
            respClass = self.__qualMessage.getClassByName(response.name)
            if respClass == None:
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
            request = []
            print "Select a module:"
            for modClassName in self.__modClass.messageMap.keys():
                for msgClassName in self.__qualMessage.messageMap.keys():
                    if msgClassName.lower().endswith("request") and modClassName.lower() == msgClassName.lower()[:-7]:
                        print "\t%d - %s" % (index, modClassName,)
                        request.append(msgClassName)
                        index += 1

            try:
                selectedModule = int(raw_input("Selection: "))
            except ValueError:
                print "Input must be a number."
                continue
            if selectedModule < 0 or selectedModule >= index:
                print "Valid range is %d to %d." % (0, index-1)
                continue
            self.runTest(request[selectedModule])






if __name__ == "__main__":
    man = QTARequestManager()
    man.runManager()

