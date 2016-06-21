import serial
import time

from common.module.module import Module
from common.gpb.python.RS232_pb2 import RS232Request, RS232Response
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.modules.rs232.rs232_Exception import RS232ModuleSerialException

## RS-232 Class Module
#
class Rs232(Module):
    ## Constructor
    #  @param       self
    #  @param       config      Configuration for the instance is going to be created
    def __init__(self, config=None):
        ## constructor of the parent class
        super(Rs232, self).__init__(config)

        self.port = '/dev/ttyUSB1'
        self.baudrate = 115200
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.bytesize = serial.EIGHTBITS
        self.loadConfig(attributes=('port','baudrate','parity','stopbits','bytesize'))

        try:
            ## open a writer serial port
            self.serial = serial.Serial(port=self.port,
                                        baudrate=self.baudrate,
                                        parity=self.parity,
                                        stopbits=self.stopbits,
                                        bytesize=self.bytesize,
                                        timeout=0.1,
                                        rtscts=True)
        except (serial.SerialException, OSError):
            raise RS232ModuleSerialException(self.port)
        else:
            # adding the message handler
            self.addMsgHandler(RS232Request, self.hdlrMsg)
            # thread that writes through RS-232
            self.addThread(self.rs232WriteRead)
            ## written characters
            self.written = 0
            ## read characters
            self.read = 0
            ## application state
            self.appState = RS232Response.STOPPED
            ## match value found
            self.match = 0
            ## mismatch value found
            self.mismatch = 0


    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param     self
    #  @param     rs232Request      tzmq format message
    #  @return    response          an RS-232 Response object
    def hdlrMsg(self, rs232Request):
        response = RS232Response()
        if rs232Request.body.requestType == RS232Request.STOP:
            response = self.stop()
        elif rs232Request.body.requestType == RS232Request.RUN:
            if self.appState == RS232Response.RUNNING:
                self.stop()
            response = self.start()
        elif rs232Request.body.requestType == RS232Request.REPORT:
            response = self.report()
        else:
            print "Unexpected request"
        return ThalesZMQMessage(response)

    ## Starts sending and reading data through RS-232
    #
    #  @param     self
    #  @return    self.report() a RS-232 Response object
    def start(self):
        # Make sure all values are cleared
        self.written = 0
        self.read = 0
        self.match = 0
        self.mismatch = 0
        self.appState = RS232Response.RUNNING
        status = self.report()
        self.startThread()
        return status

    ## Stops sending and reading data through RS-232
    #
    #  @param     self
    #  @return    self.report() a RS-232 Response object
    def stop(self):
        self._running = False
        self.stopThread()
        self.appState = RS232Response.STOPPED
        status = self.report()
        self.written = 0
        self.read = 0
        self.match = 0
        self.mismatch = 0
        return status


    ## Reports match and mismatch data
    #
    #  @param     self
    #  @return    self.report() a RS-232 Response object
    def report(self):
        # Create the response object
        status = RS232Response()
        status.state = self.appState
        status.xmtCount = self.written
        status.matches = self.match
        status.mismatches = self.mismatch
        return status

    ## Function that does all writing and reading, run in a thread
    #
    #  @param     self
    def rs232WriteRead(self):
        ## write the character current
        written = chr(self.written % 256)
        self.serial.write(written)
        self.written += 1

        ## read all written characters
        chars = []
        while True:
            char = self.serial.read()
            if char:
                chars.append(char)
            else:
                break
        self.read += len(chars)

        for index,char in enumerate(chars):
            expected =  (self.written - (len(chars)) + index) % 256
            if ord(char) != expected:
                self.mismatch += 1
            else:
                self.match += 1
