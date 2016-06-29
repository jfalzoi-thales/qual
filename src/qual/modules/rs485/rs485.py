import serial
import time

from common.module.module import Module
from common.gpb.python.RS485_pb2 import RS485Request, RS485Response
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.modules.rs485.rs485_Exception import RS485ModuleSerialException

## RS-485 Class Module
#
class Rs485(Module):
    ## Constructor
    #  @param       self
    #  @param       config      Configuration for the instance is going to be created
    def __init__(self, config=None):
        # constructor of the parent class
        super(Rs485, self).__init__(config)

        ## port
        self.port= '/dev/ttyUSB1'
        ## baud rate
        self.baudrate= 115200
        ## parity
        self.parity= serial.PARITY_NONE
        ## stop bits
        self.stopbits= serial.STOPBITS_ONE
        ## byte size
        self.bytesize= serial.EIGHTBITS
        ## timeout
        self.timeout= 3
        self.loadConfig(attributes=('port','baudrate','parity','stopbits','bytesize', 'timeout'))


        try:
            ## Serial connection
            self.serial = serial.Serial(port=self.port,
                                        baudrate=self.baudrate,
                                        parity=self.parity,
                                        stopbits=self.stopbits,
                                        bytesize=self.bytesize,
                                        timeout=self.timeout)
        except (serial.SerialException, OSError):
            raise RS485ModuleSerialException(self.port)
        else:
            # adding the message handler
            self.addMsgHandler(RS485Request, self.handlerMessage)
            # thread that writes through RS-485
            self.addThread(self.sendData)
            ## written characters
            self.written = 0
            ## application state
            self.state = RS485Response.STOPPED
            ## match value found
            self.matches = 0
            ## mismatch value found
            self.mismatches = 0
            ## character to be sent
            self.tx = chr(0)


    ## Sends the data and expects the same response
    #
    def sendData(self):
        self.serial.write(self.tx)
        self.written += 1
        # time.sleep(0.5)
        rx = self.serial.read()
        if len(rx) == 0:
            self.mismatches += 1
        elif rx != self.tx:
            self.mismatches += 1
        else:
            self.matches += 1
        ## Update the current character
        ch = ord(self.tx)+1
        if ch > 255:
            self.tx = chr(0)
        else:
            self.tx = chr(ch)

    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param     self
    #  @param     rs485Request      tzmq format message
    #  @return    response          an RS-485 Response object
    def handlerMessage(self, rs485Request):
        response = RS485Response()
        if rs485Request.body.requestType == RS485Request.STOP:
            response = self.stop()
        elif rs485Request.body.requestType == RS485Request.RUN:
            if self.state == RS485Response.RUNNING:
                self.stop()
            response = self.start()
        elif rs485Request.body.requestType == RS485Request.REPORT:
            response = self.report()
        else:
            self.log.info("Invalid Request Type Message")
        return ThalesZMQMessage(response)

    ## Starts sending and reading data through RS-485
    #
    #  @param     self
    #  @return    self.report() a RS-485 Response object
    def start(self):
        self.written = 0
        self.matches = 0
        self.mismatches = 0
        self.state = RS485Response.RUNNING
        status = self.report()
        self.startThread()
        return status

    ## Stops sending and reading data through RS-485
    #
    #  @param     self
    #  @return    self.report() a RS-485 Response object
    def stop(self):
        self._running = False
        self.state = RS485Response.STOPPED
        status = self.report()
        self.stopThread()
        self.written = 0
        self.matches = 0
        self.mismatches = 0
        return status

    ## Reports match and mismatch data
    #
    #  @param     self
    #  @return    self.report() a RS-485 Response object
    def report(self):
        status = RS485Response()
        status.state = self.state
        status.xmtCount = self.written
        status.matches = self.matches
        status.mismatches = self.mismatches
        return status

    ## Stops background thread
    #  @param     self
    def terminate(self):
        if self._running:
            self._running = False
            self.stopThread()
