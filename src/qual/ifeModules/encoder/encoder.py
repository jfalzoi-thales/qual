import subprocess
import serial
from time import sleep
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.Encoder_pb2 import EncoderRequest, EncoderResponse
from common.module.module import Module
from qual.ifeModules.encoder.encoder_Exception import EncoderModuleSerialException

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
        ## StreamActive state
        self.streamActive = False
        ## Current IP address
        self.ip = ""
        ## Current port
        self.port = ""
        ## Approaching prompt detected by reader
        self.promptImminent = False
        #  Add the thread
        self.addThread(self.serialReader)

        #  Connect to the video encoder serial control
        try:
            ## Serial connection
            self.serial = serial.Serial(port='/dev/ttyUSB2',
                                        baudrate=115200,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS,
                                        timeout=1)
        except (serial.SerialException, OSError):
            raise EncoderModuleSerialException('/dev/ttyUSB2')

        #  Write a newline to wake up the console
        self.serial.write('\n')
        #  Start the reader thread
        self.startThread()

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
            self.log.error("Unexpected Request Type %d" % msg.body.requestType)

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
            ip = val[0]
            port = val[1]

            #  TODO: Replace sleeps with checking for expected output

            #  Configure IP if it has changed
            if ip != self.ip:
                self.ip = ip
                self.log.info("Request IP")
                self.serial.write('k')
                sleep(0.5)
                self.log.info("Enter IP")
                self.serial.write(self.ip+'\n')
                sleep(1.5)

            #  Configure the Port if it has changed
            if port != self.port:
                self.port = port
                self.log.info("Request port")
                self.serial.write('l')
                sleep(0.5)
                self.log.info("Enter port")
                self.serial.write(self.port+'\n')
                sleep(1.5)

            # Send the 'start' command
            self.log.info("Request start")
            self.serial.write('s')
            #  TODO: Wait a moment and check status and only change self.state if status is not "Stopped"
            self.state = EncoderResponse.RUNNING

            #  Check the streamActive field
            status = subprocess.check_output(['videoEncoder.sh', 'status']).rstrip()
            self.log.info("Status is %s" % status)
            self.streamActive = (status == 'Running')

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
        #  Send the 'stop' command
        self.log.info("Request stop")
        self.serial.write('t')
        sleep(0.5)
        self.state = EncoderResponse.STOPPED

        #  Check the streamActive field
        status = subprocess.check_output(['videoEncoder.sh', 'status']).rstrip()
        self.log.info("Status is %s" % status)
        self.streamActive = (status == 'Running')

        #  Create the response
        response = EncoderResponse()
        response.state = self.state
        response.streamActive = self.streamActive

        return response

    ## Reports status
    #
    #  @param   self
    #  @return  EncoderResponse object
    def report(self):
        #  Check the streamActive field
        status = subprocess.check_output(['videoEncoder.sh', 'status']).rstrip()
        self.streamActive = (status == 'Running')

        #  Create the response
        response = EncoderResponse()
        response.state = self.state
        response.streamActive = self.streamActive

        return response

    ## Reads from the video encoder serial console
    #
    #  @param   self
    #  @return  void
    def serialReader(self):
        line = self.serial.readline()
        if line != "":
            #  Uncomment to watch the console output
            #  print line.rstrip()
            #  TODO: set flag to indicate when safe to send command
            if "Y -- Load Factory" in line:
                #  We're almost at the prompt - set a flag for next line
                self.promptImminent = True
            elif self.promptImminent:
                #  We've reached the line before the prompt
                self.log.info("Prompt is imminent")
                self.promptImminent = False

    ## Stops background thread
    #
    #  @param     self
    def terminate(self):
        if self._running:
            self.stopThread()
