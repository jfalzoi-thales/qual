import collections
from time import sleep
import threading

from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.GPIO_pb2 import GPIORequest, GPIOResponse
from common.gpb.python.GPIOManager_pb2 import RequestMessage, ResponseMessage
from common.module import module


## Connection info container class
class ConnectionInfo(object):
    ## Constructor
    #  @param     self
    #  @param     outputPin  Output pin name
    def __init__(self, outputPin):
        super(ConnectionInfo, self).__init__()
        ## Name of output pin that input pin will be connected to
        self.outputPin = outputPin
        ## This connection is newly set up
        self.firstCycle = True
        ## Pin state on previous half-cycle
        self.lastState = True
        ## Number of matches
        self.matches = 0
        ## Number of mismatches
        self.mismatches = 0


## GPIO Module
class GPIO(module.Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config = None):
        super(GPIO, self).__init__(config)
        # Add GPIO handler to available message handlers
        self.addMsgHandler(GPIORequest, self.handler)
        ## Named tuple type to store pin info
        self.PinInfo = collections.namedtuple("PinInfo", "func name")
        ## Dict mapping GPIO output pins to handler and handler pin name
        self.outputPins = {"GP_KYLN_OUT1": self.PinInfo(self.gpioManagerSet, "OUTPUT_1_PIN_A6"),
                           "GP_KYLN_OUT2": self.PinInfo(self.gpioManagerSet, "OUTPUT_2_PIN_B6"),
                           "GP_KYLN_OUT3": self.PinInfo(self.gpioManagerSet, "OUTPUT_3_PIN_C6"),
                           "GP_KYLN_OUT4": self.PinInfo(self.gpioManagerSet, "OUTPUT_4_PIN_D6"),
                           "GP_KYLN_OUT5": self.PinInfo(self.gpioManagerSet, "OUTPUT_5_PIN_E6"),
                           "GP_KYLN_OUT6": self.PinInfo(self.gpioManagerSet, "OUTPUT_6_PIN_E8"),
                           "GP_KYLN_OUT7": self.PinInfo(self.ifeVmQtaSet, "LLS_OUT_GP_KL_01"),
                           "GP_KYLN_OUT8": self.PinInfo(self.ifeVmQtaSet, "LLS_OUT_GP_KL_02"),
                           "GP_KYLN_OUT9": self.PinInfo(self.ifeVmQtaSet, "LLS_OUT_GP_KL_03"),
                           "VA_KYLN_OUT1": self.PinInfo(self.ifeVmQtaSet, "VA_KLOUT1"),
                           "VA_KYLN_OUT2": self.PinInfo(self.ifeVmQtaSet, "VA_KLOUT2"),
                           "VA_KYLN_OUT3": self.PinInfo(self.ifeVmQtaSet, "VA_KLOUT3"),
                           "VA_KYLN_OUT4": self.PinInfo(self.ifeVmQtaSet, "VA_KLOUT4"),
                           "VA_KYLN_OUT5": self.PinInfo(self.ifeVmQtaSet, "VA_KLOUT5"),
                           "VA_KYLN_OUT6": self.PinInfo(self.ifeVmQtaSet, "VA_KLOUT6")}

        ## Dict mapping GPIO input pins to handler and handler pin name
        self.inputPins = {"GP_KYLN_IN1": self.PinInfo(self.gpioManagerGet, "INPUT_1_PIN_A7"),
                          "GP_KYLN_IN2": self.PinInfo(self.gpioManagerGet, "INPUT_2_PIN_B7"),
                          "GP_KYLN_IN3": self.PinInfo(self.gpioManagerGet, "INPUT_3_PIN_C7"),
                          "GP_KYLN_IN4": self.PinInfo(self.gpioManagerGet, "INPUT_4_PIN_D7"),
                          "GP_KYLN_IN5": self.PinInfo(self.gpioManagerGet, "INPUT_5_PIN_E7"),
                          "PA_ALL_KYLN_IN": self.PinInfo(self.gpioManagerGet, "PA_All_PIN_C8"),
                          "GP_KYLN_IN6": self.PinInfo(self.ifeVmQtaGet, "LLS_IN_GP_KL_01"),
                          "GP_KYLN_IN7": self.PinInfo(self.ifeVmQtaGet, "LLS_IN_GP_KL_02"),
                          "GP_KYLN_IN8": self.PinInfo(self.ifeVmQtaGet, "LLS_IN_GP_KL_03"),
                          "GP_KYLN_IN9": self.PinInfo(self.ifeVmQtaGet, "LLS_IN_GP_KL_04"),
                          "PA_KYLN_IN1": self.PinInfo(self.ifeVmQtaGet, "PA_KLIN1"),
                          "PA_KYLN_IN2": self.PinInfo(self.ifeVmQtaGet, "PA_KLIN2"),
                          "PA_KYLN_IN3": self.PinInfo(self.ifeVmQtaGet, "PA_KLIN3"),
                          "PA_KYLN_IN4": self.PinInfo(self.ifeVmQtaGet, "PA_KLIN4"),
                          "PA_KYLN_IN5": self.PinInfo(self.ifeVmQtaGet, "PA_KLIN5"),
                          "PA_KYLN_IN6": self.PinInfo(self.ifeVmQtaGet, "PA_KLIN6"),
                          "PA_KYLN_IN7": self.PinInfo(self.ifeVmQtaGet, "PA_KLIN7"),
                          "PA_KYLN_IN8": self.PinInfo(self.ifeVmQtaGet, "PA_KLIN8"),
                          "PA_MUTE_KYLN_IN": self.PinInfo(self.ifeVmQtaGet, "PA_MUTE")}
        ## Dict of connections; key is input pin, value is a ConnectionInfo object
        self.connections = {}
        ## List of connections we're done with
        self.deadConnections = []
        ## Lock for access to connections dict
        self.connectionsLock = threading.Lock()
        ## Current output state used by toggleOutputs
        self.outputState = False
        ## Connection to GPIO Manager
        self.gpioMgrClient = ThalesZMQClient("ipc:///tmp/gpio-mgr.sock", log=self.log, msgParts=1)
        ## Address for communicating with QTA running on the IFE VM
        self.ifeVmQtaAddr = "tcp://localhost:50003"
        self.loadConfig(attributes=('ifeVmQtaAddr',))
        ## Connection to QTA running on the IFE VM
        self.ifeVmQtaClient = ThalesZMQClient(self.ifeVmQtaAddr, log=self.log)
        # Set up thread to toggle outputs
        self.addThread(self.toggleOutputs)

    ## Handles incoming request messages
    # @param  self
    # @param  msg       TZMQ format message
    # @return reply     a ThalesZMQMessage object containing the response message
    def handler(self, msg):
        gpioResp = GPIOResponse()

        # First validate input pin, since all request types contain one
        if msg.body.gpIn != "ALL" and str(msg.body.gpIn) not in self.inputPins:
            self.log.error("Unknown GPIO input pin %s" % msg.body.gpIn)
        elif msg.body.requestType == GPIORequest.CONNECT:
            if str(msg.body.gpOut) not in self.outputPins:
                self.log.error("Unknown GPIO output pin %s" % msg.body.gpOut)
            else:
                gpioResp = self.connect(msg.body)
        elif msg.body.requestType == GPIORequest.DISCONNECT:
            gpioResp = self.disconnect(msg.body)
        elif msg.body.requestType == GPIORequest.REPORT:
            gpioResp = self.report(msg.body)
        else:
            self.log.error("Unexpected Request Type %d" % msg.body.requestType)

        return ThalesZMQMessage(gpioResp)

    ## Handles GPIO requests with requestType of CONNECT
    # @param  self
    # @param  gpioReq  Message body with request details
    # @return a GPIOResponse message to be returned to the client
    def connect(self, gpioReq):
        # Note: pins are already validated, so we don't have to do that here.
        # If input pin is specified as "ALL", discard all existing connections and
        # connect all defined input pins to the specified output pin.
        # If input pin is not in connection list, add it with counters set to zero.
        # If input pin is already in connection list, just drop through to report.
        if gpioReq.gpIn == "ALL":
            # Get connections lock before modifying connections
            self.connectionsLock.acquire()
            self.connections.clear()

            for inputPin in self.inputPins.keys():
                self.connections[inputPin] = ConnectionInfo(str(gpioReq.gpOut))

            self.connectionsLock.release()
        elif str(gpioReq.gpIn) not in self.connections:
            # Get connections lock before modifying connections
            self.connectionsLock.acquire()
            self.connections[str(gpioReq.gpIn)] = ConnectionInfo(str(gpioReq.gpOut))
            self.connectionsLock.release()

        # If thread is not running, start it
        if not self._running:
            self.startThread()

        # Return a report
        return self.report(gpioReq)

    ## Handles GPIO requests with requestType of DISCONNECT
    # @param  self
    # @param  gpioReq  Message body with request details
    # @return a GPIOResponse message to be returned to the client
    def disconnect(self, gpioReq):
        # Note: pins are already validated, so we don't have to do that here.
        # If input pin is specified as "ALL", disconnect all inputs.
        # If input pin is in connection list, remove it.
        # If input pin is not in connection list, just drop through to report.
        inputPin = str(gpioReq.gpIn)
        if inputPin == "ALL" or inputPin in self.connections:
            # Get report before processing the disconnect
            gpioResp = self.report(gpioReq)
            # Get connections lock before modifying connections.
            self.connectionsLock.acquire()

            # Save the connection(s) we're done with in deadConnections so we can set them low
            if gpioReq.gpIn == "ALL":
                if len(self.connections) > 0:
                    self.deadConnections.extend(self.connections.values())
                    self.connections.clear()
            else:
                conn = self.connections.pop(inputPin)
                self.deadConnections.append(conn)

            self.connectionsLock.release()

            # Return the report
            return gpioResp
        # Return the report
        return self.report(gpioReq)

    ## Handles GPIO requests with requestType of REPORT
    # @param  self
    # @param  gpioReq  Message body with request details
    # @return a GPIOResponse message to be returned to the client
    def report(self, gpioReq):
        gpioResp = GPIOResponse()

        # Note: pins are already validated, so we don't have to do that here.
        if gpioReq.gpIn == "ALL":
            # Add status entries for all input pins
            for inputPin in sorted(self.inputPins.keys()):
                self.addPinStatus(gpioResp, inputPin, gpioReq.requestType == GPIORequest.DISCONNECT)
        else:
            # Add status entry for specified input pin
            self.addPinStatus(gpioResp, str(gpioReq.gpIn), gpioReq.requestType == GPIORequest.DISCONNECT)

        # Return the report
        return gpioResp

    ## Adds pin status entry to a GPIOResponse
    # @param  self
    # @param  gpioResp       Response message object
    # @param  inputPin       Input pin for which to add information to the response
    # @param  disconnecting  Indicates we are gathering info prior to a disconnect
    def addPinStatus(self, gpioResp, inputPin, disconnecting):
        gpioStatus = gpioResp.status.add()
        gpioStatus.gpIn = inputPin

        if inputPin in self.connections:
            connection = self.connections[inputPin]
            gpioStatus.matchCount = connection.matches
            gpioStatus.mismatchCount = connection.mismatches
            gpioStatus.gpOut = connection.outputPin
            # If we're disconnecting, set the connection state to disconnected
            gpioStatus.conState = GPIOResponse.DISCONNECTED if disconnecting else GPIOResponse.CONNECTED
        else:
            gpioStatus.conState = GPIOResponse.DISCONNECTED
            gpioStatus.matchCount = 0
            gpioStatus.mismatchCount = 0

    ## Run in a thread to toggle active GPIO outputs on and off every 2 seconds
    # @param  self
    def toggleOutputs(self):
        self.outputState = not self.outputState
        # Make a shallow copy of connections to reduce locking in background thread
        self.connectionsLock.acquire()
        connectionsCopy = dict.copy(self.connections)
        self.connectionsLock.release()

        # For each unique output pin in the connection list, set the new state
        for outputPin in {c.outputPin for c in connectionsCopy.values()}:
            pinInfo = self.outputPins[outputPin]
            pinInfo.func(pinInfo.name, self.outputState)

        # For each input pin in the connection list, get its value and increment matches/mismatches
        for inputPin, connection in connectionsCopy.items():
            pinInfo = self.inputPins[inputPin]
            inputState = pinInfo.func(pinInfo.name)
            # We calculate statistics every full cycle (high-low)
            if self.outputState:
                # On "high" half-cycle, just store the state
                #self.log.debug("Pin %s expect 1 got %d" % (inputPin, inputState))
                connection.lastState = inputState
                if connection.firstCycle:
                    # First full cycle for this connection has been reached, so we can clear this flag
                    connection.firstCycle = False
            else:
                # On "low" half-cycle, update the statistics
                #self.log.debug("Pin %s expect 0 got %d" % (inputPin, inputState))
                if connection.firstCycle:
                    # Connection was added mid-cycle; wait until next cycle to update stats
                    self.log.debug("Pin %s just added; waiting to update stats" % inputPin)
                elif inputState == False and connection.lastState == True:
                    connection.matches += 1
                else:
                    connection.mismatches += 1

        # Requirement MPS-SRS-272 states to toggle "at 0.5 Hz with a 50% duty cycle"
        # which I interpret as 0.5 Hz for a complete on/off cycle, or 1 second at each state.
        sleep(1)

        # Operate on a copy of dead connections to reduce locking in background thread
        self.connectionsLock.acquire()
        deadConnectionsCopy = self.deadConnections
        self.deadConnections = []
        self.connectionsLock.release()

        # For each unique output pin on the dead connection list, set it low
        # Note: An output pin might still be in use, but that's OK because it will
        # be re-set to the correct value next time through toggleOutputs()
        if len(deadConnectionsCopy) > 0:
            for outputPin in {c.outputPin for c in deadConnectionsCopy}:
                self.log.debug("Done with output %s; setting to low" % outputPin)
                pinInfo = self.outputPins[outputPin]
                pinInfo.func(pinInfo.name, False)

    ## Sets a pin state using the GPIO Manager
    # @param  self
    # @param  pinName Pin name to be sent to the GPIO manager
    # @param  state   New state to be sent to the GPIO manager
    def gpioManagerSet(self, pinName, state):
        # Create a GPIO Manager request of type SET
        setReq = RequestMessage()
        setReq.pin_name = pinName
        setReq.request_type = RequestMessage.SET
        setReq.value = state
        # Send a request and get the response
        response = self.gpioMgrClient.sendRequest(ThalesZMQMessage(setReq))

        # Parse the response
        if response.name == self.gpioMgrClient.defaultResponseName:
            setResp = ResponseMessage()
            setResp.ParseFromString(response.serializedBody)
            if setResp.error == ResponseMessage.OK:
                return

        self.log.error("Error return from GPIO Manager for pin %s" % pinName)

    ## Gets a pin state using the GPIO Manager
    # @param  self
    # @param  pinName Pin name to be sent to the GPIO manager
    # @return Current state of the pin
    def gpioManagerGet(self, pinName):
        # Create a GPIO Manager request of type GET
        getReq = RequestMessage()
        getReq.pin_name = pinName
        getReq.request_type = RequestMessage.GET

        # Send a request and get the response
        response = self.gpioMgrClient.sendRequest(ThalesZMQMessage(getReq))

        # Parse the response
        if response.name == self.gpioMgrClient.defaultResponseName:
            getResp = ResponseMessage()
            getResp.ParseFromString(response.serializedBody)
            if getResp.error == ResponseMessage.OK:
                return getResp.state

        self.log.error("Error return from GPIO Manager for pin %s" % pinName)
        # Return the opposite of the current output state to force match to fail
        return not self.outputState

    ## Sets an IFE card pin state using IFE QTA in VM
    # @param  self
    # @param  pinName Pin name to be sent to IFE QTA
    # @param  state   New state to be sent to IFE QTA
    def ifeVmQtaSet(self, pinName, state):
        # Create a GPIO Manager request of type SET
        setReq = RequestMessage()
        setReq.pin_name = pinName
        setReq.request_type = RequestMessage.SET
        setReq.value = state
        # Send a request and get the response
        response = self.ifeVmQtaClient.sendRequest(ThalesZMQMessage(setReq))

        # Parse the response
        if response.name == "ResponseMessage":
            setResp = ResponseMessage()
            setResp.ParseFromString(response.serializedBody)
            if setResp.error == ResponseMessage.OK:
                return

        self.log.error("Error return from IFE VM GPIO for pin %s" % pinName)

    ## Gets an IFE card pin state using IFE QTA in VM
    # @param  self
    # @param  pinName Pin name to be sent to IFE QTA
    # @return Current state of the pin
    def ifeVmQtaGet(self, pinName):
        # Create a GPIO Manager request of type GET
        getReq = RequestMessage()
        getReq.pin_name = pinName
        getReq.request_type = RequestMessage.GET

        # Send a request and get the response
        response = self.ifeVmQtaClient.sendRequest(ThalesZMQMessage(getReq))

        # Parse the response
        if response.name == "ResponseMessage":
            getResp = ResponseMessage()
            getResp.ParseFromString(response.serializedBody)
            if getResp.error == ResponseMessage.OK:
                return getResp.state

        self.log.error("Error return from IFE VM GPIO for pin %s" % pinName)
        # Return the opposite of the current output state to force match to fail
        return not self.outputState

    ## Stops background thread
    #  @param     self
    def terminate(self):
        if self._running:
            self.stopThread()
