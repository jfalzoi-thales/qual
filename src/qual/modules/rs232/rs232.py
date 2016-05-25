import serial
import time

from src.common.module.module import Module
from src.common.module.unitTest import BaseMessage
from src.common.gpb.python.RS232_pb2 import RS232Request, RS232Response

appState = RS232Response.AppStateT.STOPPED

class Rs232MsgHdlr(BaseMessage):
    def __init__(self, rs232Request):
        self.msg = rs232Request
        super(Rs232MsgHdlr, self).__init__()
        pass

class Rs232(Module):
    def __init__(self, config={}):
        super(Rs232, self).__init__(config)
        self.addMsgHandler(Rs232MsgHdlr, self.hdlrMsg)
        self.addThread(self.rs232Write)
        self.addThread(self.rs232Read)
        self.match = 0
        self.mismatch = 0

    @classmethod
    def getConfigurations(cls):
        return [
                {'portwriter': '/dev/ttyUSB2','portreader': '/dev/ttyUSB3', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS},
                ]

    def rs232Write(self):
        global appState
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

    def hdlrMsg(self, rs232Request):
        response = RS232Response()
        if rs232Request.requestType == RS232Request.STOP:
            response = self.stop()
        elif rs232Request.requestType == RS232Request.RUN:
            response = self.stop()
        elif rs232Request.requestType == RS232Request.STOP:
            response = self.report()
        else:
            print "Unexpected request"
        return response

    def start(self):
        global appState
        self.portWriter = self.config['portwriter']
        self.portReader = self.config['portreader']
        self.baudrate = self.config['baudrate']
        self.parity= self.config['parity']
        self.stopbits = self.config['stopbits']
        self.bytesize = self.config['bytesize']
        super(Rs232, self).startThread()
        appState = RS232Response.AppStateT.RUNNING
        status = RS232Response(appState, self.match, self.mismatch)
        return status

    def stop(self):
        global appState
        appState =RS232Response.AppStateT.STOPPED
        status = RS232Response(appState, self.match, self.mismatch)
        super(Rs232, self).stopThread()
        return status

    def report(self):
        global appState
        status = RS232Response(appState, self.match, self.mismatch)
        return status