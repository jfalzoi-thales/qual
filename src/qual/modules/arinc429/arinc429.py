import collections
from time import time, sleep
import threading
import os
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.ARINC429_pb2 import ARINC429Request, ARINC429Response
from common.gpb.python.ARINC429Driver_pb2 import Request, Response, ChannelConfig
from common.module import module

## Connection info container class
class ConnectionInfo(object):
    ## Constructor
    #  @param     self
    #  @param     outputChan  Output channel name
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
    def __init__(self, config = None):
        super(ARINC429, self).__init__(config)

        ## TX1 driver channel name (can be overridden by config)
        self.tx1Channel = "tx00"
        ## TX2 driver channel name (can be overridden by config)
        self.tx2Channel = "tx10"
        ## TX3 driver channel name (can be overridden by config)
        self.tx3Channel = "tx20"
        ## TX4 driver channel name (can be overridden by config)
        self.tx4Channel = "tx30"
        ## RX1 driver channel name (can be overridden by config)
        self.rx1Channel = "rx00"
        ## RX2 driver channel name (can be overridden by config)
        self.rx2Channel = "rx01"
        ## RX3 driver channel name (can be overridden by config)
        self.rx3Channel = "rx10"
        ## RX4 driver channel name (can be overridden by config)
        self.rx4Channel = "rx11"
        ## RX5 driver channel name (can be overridden by config)
        self.rx5Channel = "rx20"
        ## RX6 driver channel name (can be overridden by config)
        self.rx6Channel = "rx21"
        ## RX7 driver channel name (can be overridden by config)
        self.rx7Channel = "rx30"
        ## RX8 driver channel name (can be overridden by config)
        self.rx8Channel = "rx31"
        # Read config file and update specified instance variables
        self.loadConfig(attributes=('tx1Channel', 'tx2Channel', 'tx3Channel', 'tx4Channel',
                                    'rx1Channel', 'rx2Channel', 'rx3Channel', 'rx4Channel',
                                    'rx5Channel', 'rx6Channel', 'rx7Channel', 'rx8Channel'))
        ## Named tuple type to store channel info
        self.ChanInfo = collections.namedtuple("ChanInfo", "name chan")
        ## Dict mapping output channels to driver channel name and code
        self.outputChans = {"ARINC_429_TX1": self.ChanInfo(self.tx1Channel, 0),
                            "ARINC_429_TX2": self.ChanInfo(self.tx2Channel, 1),
                            "ARINC_429_TX3": self.ChanInfo(self.tx3Channel, 2),
                            "ARINC_429_TX4": self.ChanInfo(self.tx4Channel, 3)}
        ## Dict mapping input channels to driver channel name and code
        self.inputChans = {"ARINC_429_RX1":  self.ChanInfo(self.rx1Channel, 0),
                           "ARINC_429_RX2":  self.ChanInfo(self.rx2Channel, 1),
                           "ARINC_429_RX3":  self.ChanInfo(self.rx3Channel, 2),
                           "ARINC_429_RX4":  self.ChanInfo(self.rx4Channel, 3),
                           "ARINC_429_RX5":  self.ChanInfo(self.rx5Channel, 4),
                           "ARINC_429_RX6":  self.ChanInfo(self.rx6Channel, 5),
                           "ARINC_429_RX7":  self.ChanInfo(self.rx7Channel, 6),
                           "ARINC_429_RX8":  self.ChanInfo(self.rx8Channel, 7)}
        ## Counter for data incrementing
        self.increment = 0
        ## Dict of connections; key is input channel, value is a ConnectionInfo object
        self.connections = {}
        ## Lock for access to connections dict
        self.connectionsLock = threading.Lock()
        #  Ensure directory for communication with ARINC429 driver is present
        ipcdir = "/tmp/arinc/driver/429"

        if not os.path.exists(ipcdir):
            os.makedirs(ipcdir)

        ## Connection to ARINC429 driver
        self.driverClient = ThalesZMQClient("ipc:///tmp/arinc/driver/429/device", log=self.log, msgParts=1)

        # Configuring driver for all channels
        for outputChan in self.outputChans.values():
            confReq = Request()
            confReq.channelName = outputChan.name
            confReq.type = Request.SET_CONFIG
            conf = confReq.config.add()
            conf.rate = ChannelConfig.HIGH
            conf.labelOrder = ChannelConfig.NORMAL
            conf.parityEnable = False
            response = self.driverClient.sendRequest(ThalesZMQMessage(confReq))

            #  Parse the response
            if response.name == self.driverClient.defaultResponseName:
                confResp = Response()
                confResp.ParseFromString(response.serializedBody)
                self.log.info('\n%s' % confResp)

                if confResp.errorCode != Response.NONE:
                    self.log.error("Error configuring ARINC429 driver for channel %s" % outputChan.name)
                    self.log.error("ERROR CODE: %s" % confResp.errorCode)

        for inputChan in self.inputChans.values():
            confReq = Request()
            confReq.channelName = inputChan.name
            confReq.type = Request.SET_CONFIG
            conf = confReq.config.add()
            conf.rate = ChannelConfig.HIGH
            conf.labelOrder = ChannelConfig.NORMAL
            conf.parityEnable = False
            response = self.driverClient.sendRequest(ThalesZMQMessage(confReq))

            #  Parse the response
            if response.name == self.driverClient.defaultResponseName:
                confResp = Response()
                confResp.ParseFromString(response.serializedBody)
                self.log.info('\n%s' % confResp)

                if confResp.errorCode != Response.NONE:
                    self.log.error("Error configuring ARINC429 driver for channel %s" % inputChan.name)
                    self.log.error("ERROR CODE: %s" % confResp.errorCode)

        #  Set up thread to toggle outputs
        self.addThread(self.sendData)
        #  Add handler to available message handlers
        self.addMsgHandler(ARINC429Request, self.handler)

    ## Handles incoming request messages
    #  @param    self
    #  @param    msg   tzmq format message
    #  @return   a ThalesZMQMessage object containing the response message
    def handler(self, msg):
        response = ARINC429Response()

        #  First validate input channel, since all request types contain one
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
    #  @param    self
    #  @param    request     Message body with request details
    #  @param    response    ARINC429 response object
    def connect(self, request, response):
        #  Note: channels are already validated, so we don't have to do that here.
        #  If input channel is specified as "ALL", discard all existing connections and
        #  connect all defined input channels to the specified output channel.
        #  If input channel is not in connection list, add it with counters set to zero.
        #  If input channel is already in connection list, just drop through to report.
        if request.sink == "ALL":
            #  Get connections lock before modifying connections
            self.connectionsLock.acquire()
            self.connections.clear()

            for inputChan in self.inputChans.keys():
                self.connections[inputChan] = ConnectionInfo(str(request.source))
                #  Clear out any old driver responses
                self.receive(self.inputChans[inputChan].name)

            self.connectionsLock.release()
        elif str(request.sink) not in self.connections:
            #  Get connections lock before modifying connections
            self.connectionsLock.acquire()
            self.connections[str(request.sink)] = ConnectionInfo(str(request.source))
            #  Clear out any old driver responses
            self.receive(self.inputChans[request.sink].name)
            self.connectionsLock.release()

        #  If thread is not running, start it
        if not self._running:
            self.startThread()

        self.report(request, response)

    ## Handles ARINC429 requests with requestType of DISCONNECT
    #  @param    self
    #  @param    request     Message body with request details
    #  @param    response    ARINC429 response object
    def disconnect(self, request, response):
        #  Note: channels are already validated, so we don't have to do that here.
        #  If input channel is specified as "ALL", disconnect all inputs.
        #  If input channel is in connection list, remove it.
        #  If input channel is not in connection list, just drop through to report.
        if request.sink == "ALL" or str(request.sink) in self.connections:
            #  Get report before processing the disconnect
            self.report(request, response)
            #  Get connections lock before modifying connections.
            self.connectionsLock.acquire()

            if request.sink == "ALL":
                self.connections.clear()
            else:
                del self.connections[str(request.sink)]

            self.connectionsLock.release()

            if len(self.connections) == 0:
                self.stopThread()

            return

        self.report(request, response)

    ## Handles ARINC429 requests with requestType of REPORT
    #  @param    self
    #  @param    request     Message body with request details
    #  @param    response    ARINC429 response object
    def report(self, request, response):
        #  Note: channels are already validated, so we don't have to do that here.
        if request.sink == "ALL":
            #  Add status entries for all input channels
            for inputChan in sorted(self.inputChans.keys()):
                self.updateChanStatus(response, inputChan, request.requestType == ARINC429Request.DISCONNECT)
        else:
            #  Add status entry for specified input channel
            self.updateChanStatus(response, str(request.sink), request.requestType == ARINC429Request.DISCONNECT)

    ## Adds channel status entry to a ARINC429Response
    #  @param  response       ARINC429 response object
    #  @param  inputChan      Input channel for which to add information to the response
    #  @param  disconnecting  Indicates we are gathering info prior to a disconnect
    def updateChanStatus(self, response, inputChan, disconnecting):
        status = response.status.add()
        status.sink = inputChan
        status.source = ""
        self.connectionsLock.acquire()

        if inputChan in self.connections:
            connection = self.connections[inputChan]
            status.source = connection.outputChan
            status.errorCount = connection.errorCount
            status.xmtCount = connection.xmtCount
            status.rcvCount = connection.rcvCount
            #  If we're disconnecting, set the connection state to disconnected
            status.conState = ARINC429Response.DISCONNECTED if disconnecting else ARINC429Response.CONNECTED
        else:
            status.conState = ARINC429Response.DISCONNECTED
            status.xmtCount = 0
            status.rcvCount = 0
            status.errorCount = 0

        self.connectionsLock.release()

    ## Run in a thread to update incremental output
    #  @param  self
    def sendData(self):
        words = {}

        #  Increments 17 unreserved bits of data up to max and resets
        if self.increment < 131071:
            self.increment += 1
        else:
            self.increment = 0

        #  Get connections lock before accessing connections.
        self.connectionsLock.acquire()

        #  For each unique output channel in the connection list, send a word of data
        for outputChan in {c.outputChan for c in self.connections.values()}:
            chanInfo = self.outputChans[outputChan]
            word = (chanInfo.chan << 27) + (self.increment << 10)
            #  Parity bit calculation
            pbit = word^(word >> 1)
            pbit ^= pbit >> 2
            pbit = (pbit & 0x11111111) * 0x11111111
            pbit = (((pbit >> 28) & 1) + 1) & 1
            word += (pbit << 31)
            words[outputChan] = word

            if self.transmit(chanInfo.name, word):
                for connection in self.connections.values():
                    if connection.outputChan == outputChan:
                        connection.xmtCount += 1

        #  Sleep a bit before attempting to receive, to allow time for messages to arrive
        sleep(.1)

        #  For each input channel in the connection list, get its value and increment matches/mismatches
        for inputChan, connection in self.connections.items():
            chanInfo = self.inputChans[inputChan]
            reply = self.receive(chanInfo.name)

            if reply != -1:
                connection.rcvCount += 1
            if reply == -1 or reply != words[connection.outputChan]:
                connection.errorCount += 1

        #  And release the lock
        self.connectionsLock.release()
        #  If this task is too slow, decrease this delay
        #  Without this delay, sendData is capable of re-acquiring lock before other blocked functions
        sleep(.00001)

    ## Sends a transmit request to the ARINC429 Driver
    #  @param  self
    #  @param  chanName  Channel name to be sent to the ARINC429 Driver
    #  @param  output    Output to be sent from chanName through ARINC429 Driver
    #  @return           True if data transmitted successfully, False if not
    def transmit(self, chanName, output):
        #  Create a ARINC429 Driver request of type TRANSMIT_DATA
        txReq = Request()
        txReq.channelName = chanName
        txReq.type = Request.TRANSMIT_DATA
        data = txReq.outputData.data.add()
        data.word = output
        data.timestamp = int(time() * 1000)
        #  Send a request and get the response
        response = self.driverClient.sendRequest(ThalesZMQMessage(txReq))

        #  Parse the response
        if response.name == self.driverClient.defaultResponseName:
            txResp = Response()
            txResp.ParseFromString(response.serializedBody)
            self.log.info('\n%s' % txResp)

            if txResp.errorCode == Response.NONE:
                return True

        self.log.error("Error return from ARINC429 driver for channel %s" % chanName)
        return False

    ## Sends a recieve request to the ARINC429 Driver
    #  @param  self
    #  @param  chanName  Channel name to be sent to the ARINC429 Driver
    #  @return Current state of the channel
    def receive(self, chanName):
        #  Create an ARINC429 request of type RECEIVE_DATA
        rxReq = Request()
        rxReq.channelName = chanName
        rxReq.type = Request.RECEIVE_DATA
        #  Send a request and get the response
        response = self.driverClient.sendRequest(ThalesZMQMessage(rxReq))

        #  Parse the response
        if response.name == self.driverClient.defaultResponseName:
            rxResp = Response()
            rxResp.ParseFromString(response.serializedBody)
            self.log.info('\n%s' % rxResp)

            if rxResp.errorCode == Response.NONE:
                if rxResp.inputData.data:
                    return rxResp.inputData.data[0].word
                else:
                    return -1

        self.log.error("Error return from ARINC 429 driver for channel %s" % chanName)

        return -1

    ## Attempts to kill processes gracefully
    #  @param     self
    def terminate(self):
        if self._running:
            self.stopThread()