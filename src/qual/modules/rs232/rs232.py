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
        ser = serial.Serial(
            port=self.portWriter,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize
        )
        character = chr(0)
        while True:
            ser.write(character)
            time.sleep(0.5)
            if ord(character) < 255:
                character = chr(ord(character) + 1)
            else:
                character = chr(0)

    ## Opens and reads from the serial port
    #
    def rs232Read(self):
        ser = serial.Serial(
            port=self.portReader,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize
        )
        character = chr(0)
        count = 0
        while True:
            read = ser.read(1)
            if ord(read) != ord(character):
                dif = ord(read) - count
                character = read
                self.mismatch += abs(dif)
            else:
                self.match += 1
            if ord(character) < 255:
                character = chr(ord(character) + 1)
            else:
                character = chr(0)

    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param     self
    #  @param     rs232Request      tzmq format message
    #  @return    response          an RS-232 Response object
    def hdlrMsg(self, rs232Request):
        response = RS232Response()
        if rs232Request.requestType == RS232Request.STOP:
            response = self.stop()
        elif rs232Request.requestType == RS232Request.RUN:
            response = self.start()
        elif rs232Request.requestType == RS232Request.REPORT:
            response = self.report()
        else:
            print "Unexpected request"
        return ThalesZMQMessage(response)

    ## Starts sending and reading data through RS-232
    #
    #  @param     self
    #  @return    self.report() a RS-232 Response object
    def start(self):
        self.portWriter = self.config['portwriter']
        self.portReader = self.config['portreader']
        self.baudrate = self.config['baudrate']
        self.parity= self.config['parity']
        self.stopbits = self.config['stopbits']
        self.bytesize = self.config['bytesize']
        super(Rs232, self).startThread()
        self.appState = RS232Response.RUNNING
        status = RS232Response(self.appState, self.match, self.mismatch)
        return status

    ## Stops sending and reading data through RS-232
    #
    #  @param     self
    #  @return    self.report() a RS-232 Response object
    def stop(self):
        self.appState =RS232Response.STOPPED
        status = RS232Response(self.appState, self.match, self.mismatch)
        super(Rs232, self).stopThread()
        return status


    ## Reports match and mismatch data
    #
    #  @param     self
    #  @return    self.report() a RS-232 Response object
    def report(self):
        status = RS232Response(self.appState, self.match, self.mismatch)
        return status