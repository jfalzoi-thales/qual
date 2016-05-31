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
                {'portwriter': '/dev/ttyUSB2','portreader': '/dev/ttyUSB3', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS},
                ]
    ## Opens and writes to the serial port
    #
    def rs232Write(self):
        time.sleep(0.5)
        self.serWriter.write(chr(self.characters[self.idxToWrite]))
        if self.idxToWrite < 255:
            self.idxToWrite += 1
        else:
            self.idxToWrite = 0

    ## Opens and reads from the serial port
    #
    def rs232Read(self):
        read = self.serReader.read(1)
        if ord(read) != self.characters[self.idxToRead]:
            dif = ord(read) - self.characters[self.idxToRead]
            self.idxToRead = ord(read-1)
            self.mismatch += abs(dif)
        else:
            self.match += 1
        if self.idxToRead < 255:
            self.idxToRead += 1
        else:
            self.idxToRead = 0

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
        self.serWriter = serial.Serial(port=self.config['portwriter'],
                                      baudrate=self.config['baudrate'],
                                      parity=self.config['parity'],
                                      stopbits=self.config['stopbits'],
                                      bytesize=self.config['bytesize'])
        self.serReader = serial.Serial(port=self.config['portreader'],
                                      baudrate=self.config['baudrate'],
                                      parity=self.config['parity'],
                                      stopbits=self.config['stopbits'],
                                      bytesize=self.config['bytesize'])
        self.characters = range(0,256)
        self.idxToRead = 0
        self.idxToWrite = 0
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