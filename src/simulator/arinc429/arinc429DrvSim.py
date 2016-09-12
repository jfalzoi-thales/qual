import os
import sys
from ConfigParser import SafeConfigParser

from common.pb2.ARINC429Driver_pb2 import Request, Response
from tklabs_utils.logger import logger
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.tzmq.ThalesZMQServer import ThalesZMQServer


## Input info container class
class InputInfo(object):
    def __init__(self):
        super(InputInfo, self).__init__()
        ## Data is available (has been written but not read)
        self.dataAvailable = True
        ## Data word
        self.data = 0x1EFEFB00 # Start with some bogus data in the buffer
        ## Timestamp
        self.timestamp = 0
        ## Count of words written; used for error mode
        self.wordCount = 0

## ARINC 429 Driver Simulator class
#
# Implements a subset of the ARINC 429 Driver service, as specified
# in the "MPS ARINC 429 Driver ICD".  Specifically, it implements the
# Request and Response messages, with the following limitations:
#   - The channel names are taken from the Qual ICD, because the names are
#     missing from the ARINC 429 Driver ICD.
#   - Only requests of type TRANSMIT_DATA and RECEIVE_DATA are supported;
#     other request types will return NOT_SUPPORTED
#   - Only a single word is buffered between write and read channels
#   - If a TRANSMIT_DATA request contains more than one word, all but the
#     first word are silently ignored
#
# The ARINC 429 Driver ZMQ service uses IPC at ipc:///tmp/arinc/driver/429/device
# per the "MAP Network Configuration" document.
#
# In addition, ARINC 429 loopback is simulated by having a static table that
# defines output to input connections, and whenever data is transmitted on an
# output channel in that table, the data shows up on the linked input channel.
#
# Optionally, the simulator may be started with the argument "-e" which enables
# error introduction mode, which will damage the data value every 10th Tx request.
#
class ARINC429DriverSimulator(ThalesZMQServer):
    ## Constructor
    #
    def __init__(self, introduceErrors):
        # Make the directory for the IPC link, otherwise ZMQ won't init
        ipcdir = "/tmp/arinc/driver/429"
        if not os.path.exists(ipcdir):
            os.makedirs(ipcdir)

        # Now we can init the base class
        super(ARINC429DriverSimulator, self).__init__(address="ipc:///tmp/arinc/driver/429/device",
                                                      msgParts=1)

        # Turn down ThalesZMQServer debug level
        self.log.setLevel(logger.INFO)

        ## Error introduction mode is enabled
        self.introduceErrors = introduceErrors
        if self.introduceErrors:
            self.log.info("Error mode enabled: errors will be introduced every 10 words")

        #  Parse channel names from Thales ARINC429 Driver configuration file
        thalesArinc429Config = "/thales/host/config/Arinc429Driver.conf"

        configParser = SafeConfigParser()
        configParser.read(thalesArinc429Config)

        if configParser.sections() == []:
            self.log.warning("Missing or Empty Configuration File: %s" % thalesArinc429Config)

        # Dict of input channels with info for each one
        self.inputChannels = {configParser.get("receiver0:ARINC429-1", "name"): InputInfo(),
                              configParser.get("receiver1:ARINC429-1", "name"): InputInfo(),
                              configParser.get("receiver0:ARINC429-2", "name"): InputInfo(),
                              configParser.get("receiver1:ARINC429-2", "name"): InputInfo(),
                              configParser.get("receiver0:ARINC429-3", "name"): InputInfo(),
                              configParser.get("receiver1:ARINC429-3", "name"): InputInfo(),
                              configParser.get("receiver0:ARINC429-4", "name"): InputInfo(),
                              configParser.get("receiver1:ARINC429-4", "name"): InputInfo()}

        # Simulate ARINC 429 loopback by linking outputs to inputs
        self.loopbackMap = {configParser.get("transmitter0:ARINC429-1", "name"):
                            (configParser.get("receiver0:ARINC429-1", "name"),
                             configParser.get("receiver1:ARINC429-1", "name")),
                            configParser.get("transmitter0:ARINC429-1", "name"):
                            (configParser.get("receiver0:ARINC429-2", "name"),
                             configParser.get("receiver1:ARINC429-2", "name")),
                            configParser.get("transmitter0:ARINC429-1", "name"):
                            (configParser.get("receiver0:ARINC429-3", "name"),
                             configParser.get("receiver1:ARINC429-3", "name")),
                            configParser.get("transmitter0:ARINC429-1", "name"):
                            (configParser.get("receiver0:ARINC429-4", "name"),
                             configParser.get("receiver1:ARINC429-4", "name"))}

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleRequest(self, request):
        # Route messages based on type
        if request.name == self.defaultRequestName:
            return self.handleARINC429Req(request)
        else:
            print "Error! Unsupported request type"
            return self.getUnsupportedMessageErrorResponse()

    ## Handle request of type "Request"
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleARINC429Req(self, request):
        # Parse request
        arincReq = Request()
        arincReq.ParseFromString(request.serializedBody)

        # Create a Response message for the results
        arincResp = Response()
        arincResp.channelName = arincReq.channelName

        if arincReq.type == Request.RECEIVE_DATA:
            arincResp.type = Response.INPUT_DATA
            if arincReq.channelName not in self.inputChannels:
                print "RX Request with unknown input channel:", arincReq.channelName
                arincResp.errorCode = Response.INVALID_CHANNEL
            else:
                # print "RX request:", arincReq.channelName
                arincResp.errorCode = Response.NONE
                arincResp.inputData.overwrite = False
                inputInfo = self.inputChannels[str(arincReq.channelName)]
                if inputInfo.dataAvailable:
                    word = arincResp.inputData.data.add()
                    word.word = inputInfo.data
                    word.timestamp = inputInfo.timestamp
                    # Data has been read, so set dataAvailable to False
                    inputInfo.dataAvailable = False

        elif arincReq.type == Request.TRANSMIT_DATA:
            arincResp.type = Response.STATUS
            if str(arincReq.channelName) not in self.loopbackMap:
                print "TX Request with unknown output channel:", arincReq.channelName
                arincResp.errorCode = Response.INVALID_CHANNEL
            else:
                # print "TX request:", arincReq.channelName, ":", arincReq.outputData.data[0].word
                arincResp.errorCode = Response.NONE
                # "Write" to each of the linked RX channels
                for inputName in self.loopbackMap[str(arincReq.channelName)]:
                    inputInfo = self.inputChannels[inputName]
                    inputInfo.wordCount += 1
                    if self.introduceErrors and inputInfo.wordCount % 10 == 0:
                        #print "Introducing error on channel %s data 0x%x" % (inputName, arincReq.outputData.data[0].word)
                        inputInfo.data = arincReq.outputData.data[0].word | 0x1FFFFB00
                    else:
                        inputInfo.data = arincReq.outputData.data[0].word
                    inputInfo.timestamp = arincReq.outputData.data[0].timestamp
                    inputInfo.dataAvailable = True


        elif arincReq.type == Request.GET_CONFIG:
            arincResp.type = Response.CONFIG
            arincResp.errorCode = Response.NOT_SUPPORTED

        elif arincReq.type == Request.SET_CONFIG:
            arincResp.type = Response.STATUS
            arincResp.errorCode = Response.NONE

        else:
            print "Request with unknown/unsupported request type:", arincReq.type
            arincResp.type = Response.STATUS
            arincResp.errorCode = Response.NOT_SUPPORTED

        # Send response back to client
        return ThalesZMQMessage(arincResp)


if __name__ == "__main__":
    # Command-line argument can be used to specify whether to introduce errors
    introduceErrors = False
    if len(sys.argv) > 1 and sys.argv[1] == "-e":
        introduceErrors = True
    simulator = ARINC429DriverSimulator(introduceErrors)
    simulator.run()
    print "Exit ARINC429Driver simulator"
