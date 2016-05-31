import time
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.CPULoading_pb2 import CPULoadingRequest, CPULoadingResponse
from common.gpb.python.RS232_pb2 import RS232Request, RS232Response
from common.gpb.python.MemoryBandwidth_pb2 import MemoryBandwidthRequest, MemoryBandwidthResponse
from common.classFinder.classFinder import ClassFinder
from common.module.module import Module
from google.protobuf.message import Message
from common.logger.logger import Logger

## QTARequestManager
#  Manage different type request to QTA Application
class QTARequestManager(ThalesZMQClient):
    def __init__(self):
        super(QTARequestManager, self).__init__("tcp://localhost:50001")
        self.__modClass = ClassFinder(rootPath='qual.modules',
                                     baseClass=Module)
        self.__qaulMessage = ClassFinder(rootPath='common.gpb.python',
                                     baseClass=Message)

    def runTest(self, msgClassName):
        msgClass = self.__qaulMessage.getClassByName(msgClassName)
        msg = msgClass()
        print ""
        while True:
            try:
                time.sleep(0.5)
                print ("Choose an action:\n\t0 - Stop\n\t1 - Run\n\t2 - Report")
                action = int(raw_input("Selection: "))
            except ValueError:
                print "Input must be a number."
                continue
            if action < 0 or action > 2:
                print "Valid range is 0 to 2."
                continue
            print
            if action == 0:
                msg.requestType = msgClass.STOP
            elif action == 1:
                msg.requestType = msgClass.RUN
            else:
                msg.requestType = msgClass.REPORT

            response = self.sendRequest(ThalesZMQMessage(msg))
            respClass = self.__qaulMessage.getClassByName(response.name)
            log = Logger(name="Test " + response.name[:-8])
            if respClass == None:
                log.error("Unexpected Value response")
            else:
                respMsg = respClass()
                respMsg.ParseFromString(response.serializedBody)
                log.info(respMsg)

    def runManager(self):
        index = 0
        request = []
        print "Select a module:"
        for modClassName in self.__modClass.messageMap.keys():
            for msgClassName in self.__qaulMessage.messageMap.keys():
                if msgClassName.lower().endswith("request") and modClassName.lower() == msgClassName.lower()[:-7]:
                    print "\t%d - %s" % (index, modClassName,)
                    request.append(msgClassName)
                    index += 1
        while True:
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

