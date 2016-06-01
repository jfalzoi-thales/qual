import serial
import time

from common.module.module import Module
from common.gpb.python.RS232_pb2 import RS232Request, RS232Response
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage

## RS-232 Class Module
#
class Rs232(Module):
    ## Constructor
    #  @param       self
    #  @param       config      Configuration for the instance is going to be created
    def __init__(self, config={}):
        ## constructor of the parent class
        super(Rs232, self).__init__(config)
        ## open a writer serial port
        self.serWriter = serial.Serial(port=self.config['portwriter'],
                                      baudrate=self.config['baudrate'],
                                      parity=self.config['parity'],
                                      stopbits=self.config['stopbits'],
                                      bytesize=self.config['bytesize'],
                                      rtscts=True)
        ## open a reader serial port
        self.serReader = serial.Serial(port=self.config['portreader'],
                                      baudrate=self.config['baudrate'],
                                      parity=self.config['parity'],
                                      stopbits=self.config['stopbits'],
                                      bytesize=self.config['bytesize'],
                                      rtscts=True)
        ## adding the message handler
        self.addMsgHandler(RS232Request, self.hdlrMsg)
        ## thread that writes through RS-232
        self.addThread(self.rs232Write)
        ## thread that reads through RS-232
        self.addThread(self.rs232Read)
        ## init the application state
        self.appState = RS232Response.STOPPED
        ## init match value found
        self.match = 0
        ## init mismatch value found
        self.mismatch = 0

    @classmethod
    ## Returns the test configurations for that module
    #
    #  @return      test configurations
    def getConfigurations(cls):
        return [
                {'portwriter': '/dev/ttyUSB4','portreader': '/dev/ttyUSB5', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS},
                ]
    ## Opens and writes to the serial port
    #
    def rs232Write(self):
        time.sleep(0.05)
        self.serWriter.write(self.character)
        self.written += 1
        if ord(self.character) + 1 > 255:
            self.character = chr(0)
        else:
            self.character = chr(ord(self.character) + 1)

    ## Opens and reads from the serial port
    #
    def rs232Read(self):
        read = self.serReader.read(1)
        if ord(read) != (self.read % 256):
            self.mismatch += self.written - self.read
            self.read += self.written - self.read
        else:
            self.match += 1
            self.read += 1

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
        self.character = chr(0)
        self.written = 0
        self.read = 0
        self.match = 0
        self.mismatch = 0
        super(Rs232, self).startThread()
        self.appState = RS232Response.RUNNING
        status = RS232Response()
        status.state = self.appState
        status.matches = self.match
        status.mismatches = self.mismatch
        return status

    ## Stops sending and reading data through RS-232
    #
    #  @param     self
    #  @return    self.report() a RS-232 Response object
    def stop(self):
        self._running = False
        self.appState =RS232Response.STOPPED
        status = RS232Response()
        status.state = self.appState
        status.matches = self.match
        status.mismatches = self.mismatch
        super(Rs232, self).stopThread()
        return status


    ## Reports match and mismatch data
    #
    #  @param     self
    #  @return    self.report() a RS-232 Response object
    def report(self):
        status = RS232Response()
        status.state = self.appState
        status.matches = self.match
        status.mismatches = self.mismatch
        return status