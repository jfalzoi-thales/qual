import serial
import logging
import time

from common.module.module import Module
from common.gpb.python.RS485_pb2 import RS485Request, RS485Response
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger

## RS-485 Class Module
#
class Rs485(Module):
    ## Constructor
    #  @param       self
    #  @param       config      Configuration for the instance is going to be created
    def __init__(self, config={}):
        ## constructor of the parent class
        super(Rs485, self).__init__(config)
        self.serial = serial.Serial(port=self.config['port'],
                                       baudrate=self.config['baudrate'],
                                       parity=self.config['parity'],
                                       stopbits=self.config['stopbits'],
                                       bytesize=self.config['bytesize'],
                                       timeout=self.config['timeout'])
        ## Log obj
        self.log = Logger(name="Test RS-485", level=logging.DEBUG)
        ## adding the message handler
        self.addMsgHandler(RS485Request, self.handlerMessage)
        ## thread that writes through RS-485
        self.addThread(self.sendData)
        ## init the application state
        self.state = RS485Response.STOPPED
        ## init match value found
        self.matches = 0
        ## init mismatch value found
        self.mismatches = 0
        ## character to be sent
        self.tx = chr(0)

    @classmethod
    ## Returns the test configurations for that module
    #
    #  @return      test configurations
    def getConfigurations(cls):
        return [
                {'port': '/dev/ttyUSB4', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS, 'timeout': 3},
                ]
    ## Sends the data and expects the same response
    #
    def sendData(self):
        self.serial.write(self.tx)
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
        self.startThread()
        self.matches = 0
        self.mismatches = 0
        self.state = RS485Response.RUNNING
        status = RS485Response()
        status.state = self.state
        status.matches = self.matches
        status.mismatches = self.mismatches
        return status

    ## Stops sending and reading data through RS-485
    #
    #  @param     self
    #  @return    self.report() a RS-485 Response object
    def stop(self):
        self._running = False
        self.appState =RS485Response.STOPPED
        status = RS485Response()
        status.state = self.state
        status.matches = self.matches
        status.mismatches = self.mismatches
        self.stopThread()
        return status

    ## Reports match and mismatch data
    #
    #  @param     self
    #  @return    self.report() a RS-485 Response object
    def report(self):
        status = RS485Response()
        status.state = self.state
        status.matches = self.matches
        status.mismatches = self.mismatches
        return status