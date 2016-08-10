import subprocess
import serial
import threading
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.Encoder_pb2 import EncoderRequest, EncoderResponse
from common.module.module import Module

## Video Encoder Module Class
class IFEEncoder(Module):
    ## Constructor
    #
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        #  Initializes parent class
        super(IFEEncoder, self).__init__(config)
        #  Add Encoder Message handler
        self.addMsgHandler(EncoderRequest, self.handler)
        #  State default state
        self.state = EncoderResponse.STOPPED
        #  StreamActive default state
        self.streamActive = False
        #  Add the thread
        self.addThread(self.serialControl)
        #  Connect to the video encoder serial control
        try:
            ## Serial connection
            self.serial = serial.Serial(port='/dev/ttyUSB2',
                                        baudrate=115200,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS)
        except Exception:
            self.log.error("Unable to connect to video encoder serial.")

    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  EncoderResponse object
    def handler(self, msg):
        response = EncoderResponse()
        if msg.body.requestType == EncoderRequest.RUN:
            response = self.start(msg.body.sink)
        elif msg.body.requestType == EncoderRequest.STOP:
            #  "sink" is ignored if STOP
            response = self.stop()
        elif msg.body.requestType == EncoderRequest.REPORT:
            #  "sink" is ignored if REPORT
            response = self.report()
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        return ThalesZMQMessage(response)

    ## Starts video encoder
    #
    #  @param   self
    #  @return  EncoderResponse object
    def start(self, sink):
        #  validate <IP>:<PORT>
        val = sink.split(':')
        if len(val) != 2:
            self.log.error("Wrong sink passed.")
        else:
            self.ip = val[0]
            self.port = val[1]
            self.startThread()
            self.state = EncoderResponse.RUNNING
            #  check the streamActive field
            output = subprocess.check_output(['videoEncoder', 'status'])
            if output == 'Running':
                self.streamActive = True
            else:
                self.streamActive = False
        #  Create the response
        response = EncoderResponse()
        response.state = self.state
        response.streamActive = self.streamActive

        return response

    ## Stops video encoder
    #
    #  @param   self
    #  @return  EncoderResponse object
    def stop(self):
        #  Stop the thread
        self._running = False
        self.stopThread()
        #  Send the 'stop' command
        self.serial.write('t')
        self.state = EncoderResponse.STOPPED
        #  check the streamActive field
        output = subprocess.check_output(['videoEncoder', 'status'])
        if output == 'Running':
            self.streamActive = True
        else:
            self.streamActive = False
        # Create the response
        response = EncoderResponse()
        response.state = self.state
        response.streamActive = self.streamActive

        return response

    ## Reports status
    #
    #  @param   self
    #  @return  EncoderResponse object
    def report(self):
        output = subprocess.check_output(['videoEncoder', 'status'])
        if output in ['Running','Started','Restarted']:
            self.state = EncoderResponse.RUNNING
        else:
            self.state = EncoderResponse.STOPPED
        if output == 'Running':
            self.streamActive = True
        else:
            self.streamActive = False
        # Create the response
        response = EncoderResponse()
        response.state = self.state
        response.streamActive = self.streamActive

        return response

    ## Runs the video encoder serial control
    #
    #  @param   self
    #  @return  void
    def serialControl(self):
        if isinstance(self.serial, serial.Serial):
            #  Configure IP
            self.serial.write('k')
            self.serial.write(self.ip+'\n')
            #  Configure the Port
            self.serial.write('l')
            self.serial.write(self.port+'\n')
            #  Start
            self.serial.write('s')
            #  Now, we'll read all from the serial port
            while True:
                #  Add print here for debugging
                self.serial.read()
        else:
            self.log.error("No video encoder serial control.")


    ## Stops background thread
    #
    #  @param     self
    def terminate(self):
        if self._running:
            self.stopThread()
