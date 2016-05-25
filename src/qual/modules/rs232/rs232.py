from threading import Thread
import serial
import time

from src.common.module.module import Module
from src.common.module.unitTest import BaseMessage

class StartMessage(BaseMessage):
    def __init__(self, ports):
        self.writer = ports.writer
        self.reader = ports.reader
        super(StartMessage, self).__init__()
        pass

class StopMessage(BaseMessage):
    def __init__(self):
        super(StopMessage, self).__init__()
        pass

class RequestReportMessage(BaseMessage):
    def __init__(self):
        super(RequestReportMessage, self).__init__()
        pass

class StatusRequestMessage(BaseMessage):
    def __init__(self, match, mismatch):
        self.match = match
        self.mismatch = mismatch
        super(StatusRequestMessage, self).__init__()
        pass

class PortMsg():
    def __init__(self, writer, reader):
        self.writer = writer
        self.reader = reader

class Rs232(Module):
    def __init__(self, config={}):
        super(Rs232, self).__init__(config)
        self.addMsgHandler(StartMessage, self.start)
        self.addMsgHandler(StopMessage, self.stop)
        self.addMsgHandler(RequestReportMessage, self.report)
        self.addThread(self.rs232Write)
        self.addThread(self.rs232Read)
        self.match = 0
        self.mismatch = 0

    @classmethod
    def getConfigurations(cls):
        return [
                {'port': '/dev/ttyUSB1', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS},
                {'port': '/dev/ttyUSB1', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS},
                {'port': '/dev/ttyUSB2', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS},
                {'port': '/dev/ttyUSB3', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS},
                {'port': '/dev/ttyUSB4', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS},
                {'port': '/dev/ttyUSB5', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS},
                {'port': '/dev/ttyUSB6', 'baudrate': 115200, 'parity': serial.PARITY_NONE, 'stopbits': serial.STOPBITS_ONE, 'bytesize': serial.EIGHTBITS},
                ]

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

    def start(self, msg):
        self.portWriter = msg.writer
        self.portReader = msg.reader
        self.baudrate = self.config['baudrate']
        self.parity= self.config['parity']
        self.stopbits = self.config['stopbits']
        self.bytesize = self.config['bytesize']
        super(Rs232, self).startThread()
        status = StatusRequestMessage(self.match, self.mismatch)
        return status

    def stop(self, msg):
        status = StatusRequestMessage(self.match, self.mismatch)
        super(Rs232, self).stopThread()
        return status

    def report(self, msg):
        status = StatusRequestMessage(self.match, self.mismatch)
        return status


