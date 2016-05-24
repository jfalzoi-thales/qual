from threading import Thread
import serial

from src.common.gpb.python.baseMessage import BaseMessage
from src.common.module.module import Module

match = 0
mismatch = 0

class StartMessage(BaseMessage):
    def __init__(self):
        super(StartMessage, self).__init__()

class StopMessage(BaseMessage):
    def __init__(self):
        super(StopMessage, self).__init__()

class RequestReportMessage(BaseMessage):
    def __init__(self):
        super(RequestReportMessage, self).__init__()

class StatusRequestMessage(BaseMessage):
    def __init__(self, match, mismatch):
        super(StatusRequestMessage, self).__init__()

class Rs232(Module):
    def __init__(self, config={}):
        super(Rs232, self).__init__(config)

class SerialReceiver(Thread):
    def __init__(self, config={}):
        Thread.__init__(self)
        self.com = serialStr
        self.match = 0
        self.mismatch = 0
        self.ser = serial.Serial(
            port=serialStr,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            xonxoff=8
        )
    def processData(self):
        global mismatch
        global match
        character = chr(0)
        count = 0
        while True:
            read = self.ser.read(1)
            if ord(read) != ord(character):
                dif = ord(read)-count
                character = read
                mismatch += abs(dif)
                print "Test count=" + str(match + mismatch) + ", Mismatch: " + str(read)
            else:
                match += 1
                print "Test count=" + str(match + mismatch) + ", Match: " + str(read)
            if ord(character) < 255:
                character = chr(ord(character) + 1)
                count += 1
            else:
                character = chr(0)
                count = 0

    def run(self):
        self.processData()


class Serialsender(Thread):
    def __init__(self, serialStr='0'):
        Thread.__init__(self)
        self.serialStr = serialStr
        self.match = 0
        self.mismatch = 0
        self.ser = serial.Serial(
            port=serialStr,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            xonxoff=1
        )
    def sendData(self):
        character = chr(0)
        while True:
            self.ser.write(character)
            character = chr(ord(character)+1)
            if ord(character) >= 255:
                character = chr(0)
    def run(self):
        self.sendData()

serReceiver = SerialReceiver(serialStr='/dev/ttyUSB5')
serReceiver.start()

serSender = Serialsender(serialStr='/dev/ttyUSB6')
serSender.start()