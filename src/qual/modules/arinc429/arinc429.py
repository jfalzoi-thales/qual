import collections
from time import sleep, time
import threading
import os
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.ARINC429_pb2 import ARINC429Request, ARINC429Response
from common.gpb.python.ARINC429Driver_pb2 import Request, Response
from common.module import module

## Connection info container class
class ConnectionInfo(object):
    def __init__(self, outputChan):
        super(ConnectionInfo, self).__init__()
        ## Name of output channel that input channel will be connected to
        self.outputChan = outputChan
        ## Number of transmits
        self.xmtCount = 0
        ## Number of recieves
        self.rcvCount = 0
        ## Number of errors
        self.errorCount = 0

## ARINC429 Module
class ARINC429(module.Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config = {}):
        super(ARINC429, self).__init__({})
        ## Add handler to available message handlers
        self.addMsgHandler(ARINC429Request, self.handler)

        ## Named tuple type to store channel info
        self.ChanInfo = collections.namedtuple("ChanInfo", "name chan")

        ## Dict mapping output channels to handler and handler channel name
        self.outputChans = {"ARINC_429_TX1": self.ChanInfo("ARINC_429_TX1", 0),
                           "ARINC_429_TX2": self.ChanInfo("ARINC_429_TX2", 1),
                           "ARINC_429_TX3": self.ChanInfo("ARINC_429_TX3", 2),
                           "ARINC_429_TX4": self.ChanInfo("ARINC_429_TX4", 3)}

        ## Dict mapping input channels to handler and handler channel name
        self.inputChans = {"ARINC_429_RX1":  self.ChanInfo("ARINC_429_RX1", 0),
                          "ARINC_429_RX2":  self.ChanInfo("ARINC_429_RX2", 1),
                          "ARINC_429_RX3":  self.ChanInfo("ARINC_429_RX3", 2),
                          "ARINC_429_RX4":  self.ChanInfo("ARINC_429_RX4", 3),
                          "ARINC_429_RX5":  self.ChanInfo("ARINC_429_RX5", 4),
                          "ARINC_429_RX6":  self.ChanInfo("ARINC_429_RX6", 5),
                          "ARINC_429_RX7":  self.ChanInfo("ARINC_429_RX7", 6)}

        ## Counter for data incrementing
        self.output = 0
        ## Dict of connections; key is input channel, value is a ConnectionInfo object
        self.connections = {}

        ## Lock for access to connections dict
        self.connectionsLock = threading.Lock()

        #  Ensure directory for communication with ARINC717 driver is present
        ipcdir = "/tmp/arinc/driver/429"
        if not os.path.exists(ipcdir):
            os.makedirs(ipcdir)

        ## Connection to ARINC429 driver
        self.driverClient = ThalesZMQClient("ipc:///tmp/arinc/driver/429/device")

        # Set up thread to toggle outputs
        self.addThread(self.sendData)


    ## Handles incoming request messages
    #
    # @param  self
    # @param  msg       TZMQ format message
    # @return reply     a ThalesZMQMessage object containing the response message
    def handler(self, msg):
        response = ARINC429Response()

        # First validate input channel, since all request types contain one
        if msg.body.sink != "ALL" and str(msg.body.sink) not in self.inputChans:
            self.log.error("Unknown ARINC429 input channel %s" % msg.body.sink)
        elif msg.body.requestType == ARINC429Request.CONNECT:
            if str(msg.body.source) not in self.outputChans:
                self.log.error("Unknown ARINC429 output channel %s" % msg.body.source)
            else:
                self.connect(msg.body, response)
        elif msg.body.requestType == ARINC429Request.DISCONNECT:
            self.disconnect(msg.body, response)
        elif msg.body.requestType == ARINC429Request.REPORT:
            self.report(msg.body, response)
        else:
            self.log.error("Unexpected Request Type %d" % msg.body.requestType)

        return ThalesZMQMessage(response)

    ## Handles ARINC429 requests with requestType of CONNECT
    #
    # @param    self
    # @param    request     Message body with request details
    # @param    response    ARINC429 response object
    def connect(self, request, response):
        # Note: channels are already validated, so we don't have to do that here.
        # If input channel is specified as "ALL", discard all existing connections and
        # connect all defined input channels to the specified output channel.
        # If input channel is not in connection list, add it with counters set to zero.
        # If input channel is already in connection list, just drop through to report.
        if request.sink == "ALL":
            # Get connections lock before modifying connections
            self.connectionsLock.acquire()
            self.connections.clear()
            for inputChan in self.inputChans.keys():
                self.connections[inputChan] = ConnectionInfo(str(request.source))
            self.connectionsLock.release()
        elif str(request.sink) not in self.connections:
            # Get connections lock before modifying connections
            self.connectionsLock.acquire()
            self.connections[str(request.sink)] = ConnectionInfo(str(request.source))
            self.connectionsLock.release()

        # If thread is not running, start it
        if not self._running:
            self.startThread()



        # Report
        self.report(request, response)

    ## Handles ARINC429 requests with requestType of DISCONNECT
    #
    # @param    self
    # @param    request     Message body with request details
    # @param    response    ARINC429 response object
    def disconnect(self, request, response):
        # Note: channels are already validated, so we don't have to do that here.
        # If input channel is specified as "ALL", disconnect all inputs.
        # If input channel is in connection list, remove it.
        # If input channel is not in connection list, just drop through to report.
        if request.sink == "ALL" or str(request.sink) in self.connections:
            # Get report before processing the disconnect
            self.report(request, response)

            # Get connections lock before modifying connections.
            self.connectionsLock.acquire()
            if request.sink == "ALL":
                self.connections.clear()
            else:
                del self.connections[str(request.sink)]
            self.connectionsLock.release()

        # Report
        self.report(request, response)

    ## Handles ARINC429 requests with requestType of REPORT
    #
    # @param    self
    # @param    request     Message body with request details
    # @param    response    ARINC429 response object
    def report(self, request, response):
        # Note: channels are already validated, so we don't have to do that here.
        if request.sink == "ALL":
            # Add status entries for all input channels
            for inputChan in sorted(self.inputChans.keys()):
                self.updateChanStatus(response, inputChan, request.requestType == ARINC429Request.DISCONNECT)
        else:
            # Add status entry for specified input channel
            self.updateChanStatus(response, str(request.sink), request.requestType == ARINC429Request.DISCONNECT)

    ## Adds channel status entry to a ARINC429Response
    #
    # @param  response       ARINC429 response object
    # @param  inputChan      Input channel for which to add information to the response
    # @param  disconnecting  Indicates we are gathering info prior to a disconnect
    def updateChanStatus(self, response, inputChan, disconnecting):
        status = response.status.add()
        status.sink = inputChan
        status.source = ""

        if inputChan in self.connections:
            connection = self.connections[inputChan]
            status.source = connection.outputChan
            status.errorCount = connection.errorCount
            status.xmtCount = connection.xmtCount
            status.rcvCount = connection.rcvCount
            # If we're disconnecting, set the connection state to disconnected
            status.conState = ARINC429Response.DISCONNECTED if disconnecting else ARINC429Response.CONNECTED
        else:
            status.conState = ARINC429Response.DISCONNECTED
            status.xmtCount = 0
            status.rcvCount = 0
            status.errorCount = 0

    ## Run in a thread to send incremental output
    #
    # @param  self
    def sendData(self):
        word = 0
        # increments 17 unreserved bits of data up to max and resets
        if self.output < 131071:
            self.output += 1
        else:
            self.output = 0

        # Get connections lock before accessing connections.
        self.connectionsLock.acquire()
        # For each unique output channel in the connection list, set the new state
        for outputChan in {c.outputChan for c in self.connections.values()}:
            chanInfo = self.outputChans[outputChan]
            word = (chanInfo.chan << 27) + (self.output << 10)
            # Parity bit calculation
            pbit = word^(word >> 1)
            pbit ^= pbit >> 2
            pbit = (pbit & 0x11111111) * 0x11111111
            pbit = (((pbit >> 28) & 1) + 1) & 1

            word = (pbit << 31) + word

            self.transmit(chanInfo.name, word)

            for connection in self.connections.values():
                if connection.outputChan == outputChan:
                    connection.xmtCount += 1

        # For each input channel in the connection list, get its value and increment matches/mismatches
        for inputChan, connection in self.connections.items():
            chanInfo = self.inputChans[inputChan]
            if self.receive(chanInfo.name) == word:
                connection.rcvCount += 1
            else:
                connection.errorCount += 1
        # And release the lock
        self.connectionsLock.release()

        # Requirement MPS-SRS-272 states to toggle "at 0.5 Hz with a 50% duty cycle"
        # which I interpret as 0.5 Hz for a complete on/off cycle, or 1 second at each state.
        sleep(1)

    ## Sends a transmit request to the ARINC429 Driver
    #
    # @param  self
    # @param  chanName  Channel name to be sent to the ARINC429 Driver
    # @param  output    Output to be sent from chanName through ARINC429 Driver
    def transmit(self, chanName, output):
        # Create a ARINC429 Driver request of type TRANSMIT_DATA
        txReq = Request()
        txReq.channelName = chanName
        txReq.type = Request.TRANSMIT_DATA
        data = txReq.outputData.data.add()
        data.data = output
        data.timestamp = int(time() * 1000)

        # Send a request and get the response
        print("BOOP")
        response = self.driverClient.sendRequest(ThalesZMQMessage(txReq))
        print("BOOP2")
        # Parse the response
        if response.name == "Response":
            txResp = Response()
            txResp.ParseFromString(response.serializedBody)
            if txResp.errorCode == Response.NONE:
                return

        self.log.error("Error return from ARINC429 driver for channel %s" % chanName)

    ## Sends a recieve request to the ARINC429 Driver
    #
    # @param  self
    # @param  chanName  Channel name to be sent to the ARINC429 Driver
    # @return Current state of the channel
    def receive(self, chanName):
        # Create an ARINC429 request of type RECEIVE_DATA
        rxReq = Request()
        rxReq.channelName = chanName
        rxReq.type = Request.RECEIVE_DATA

        # Send a request and get the response
        response = self.driverClient.sendRequest(ThalesZMQMessage(rxReq))

        # Parse the response
        if response.name == "Response":
            rxResp = Response()
            rxResp.ParseFromString(response.serializedBody)
            if rxResp.errorCode == Response.NONE:
                if rxResp.inputData.data:
                    return rxResp.inputData.data[0].data
                else:
                    return

        self.log.error("Error return from GPIO Manager for channel %s" % chanName)
        return False

    ## Attempts to kill processes gracefully
    #  @param     self
    def terminate(self):
        if self._running:
            self.stopThread()