
import sys
import os
from common.tzmq.ThalesZMQServer import ThalesZMQServer
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.ARINC429Driver_pb2 import Request, Response


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
        super(ARINC429DriverSimulator, self).__init__("ipc:///tmp/arinc/driver/429/device")
        print "Started ARINC429Driver simulator on", self.address

        ## Error introduction mode is enabled
        self.introduceErrors = introduceErrors

        # Dict of input channels with info for each one
        self.inputChannels = {"ARINC_429_RX1": InputInfo(),
                              "ARINC_429_RX2": InputInfo(),
                              "ARINC_429_RX3": InputInfo(),
                              "ARINC_429_RX4": InputInfo(),
                              "ARINC_429_RX5": InputInfo(),
                              "ARINC_429_RX6": InputInfo(),
                              "ARINC_429_RX7": InputInfo()}

        # Simulate ARINC 429 loopback by linking outputs to inputs
        self.loopbackMap = {"ARINC_429_TX1": ("ARINC_429_RX1", "ARINC_429_RX2"),
                            "ARINC_429_TX2": ("ARINC_429_RX3", "ARINC_429_RX4"),
                            "ARINC_429_TX3": ("ARINC_429_RX5", "ARINC_429_RX6"),
                            "ARINC_429_TX4": ("ARINC_429_RX7",)}

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleRequest(self, request):
        # Route messages based on type
        if request.name == "Request":
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
                    word.data = inputInfo.data
                    word.timestamp = inputInfo.timestamp
                    # Data has been read, so set dataAvailable to False
                    inputInfo.dataAvailable = False

        elif arincReq.type == Request.TRANSMIT_DATA:
            arincResp.type = Response.STATUS
            if str(arincReq.channelName) not in self.loopbackMap:
                print "TX Request with unknown output channel:", arincReq.channelName
                arincResp.errorCode = Response.INVALID_CHANNEL
            else:
                # print "TX request:", arincReq.channelName, ":", arincReq.outputData.data[0].data
                arincResp.errorCode = Response.NONE
                # "Write" to each of the linked RX channels
                for inputName in self.loopbackMap[str(arincReq.channelName)]:
                    inputInfo = self.inputChannels[inputName]
                    inputInfo.wordCount += 1
                    if self.introduceErrors and inputInfo.wordCount % 10 == 0:
                        print "Introducing error on channel %s data 0x%x" % (inputName, arincReq.outputData.data[0].data)
                        inputInfo.data = arincReq.outputData.data[0].data | 0x1FFFFB00
                    else:
                        inputInfo.data = arincReq.outputData.data[0].data
                    inputInfo.timestamp = arincReq.outputData.data[0].timestamp
                    inputInfo.dataAvailable = True

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
        print "Error mode enabled: errors will be introduced every 10 words"
        introduceErrors = True
    simulator = ARINC429DriverSimulator(introduceErrors)
    simulator.run()
    print "Exit ARINC429Driver simulator"
