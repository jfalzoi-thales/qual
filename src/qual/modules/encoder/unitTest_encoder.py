import subprocess
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
        #  InputActive default state
        self.inputActive = False
        #  StreamActive default state
        self.streamActive = False

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
            #  According to ICD "sink" is ignored if STOP
            response = self.stop()
        elif msg.body.requestType == EncoderRequest.REPORT:
            #  According to ICD "sink" is ignored if REPORT
            response = self.report()
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        return ThalesZMQMessage(response)

    ## Starts video encoder
    #
    #  @param   self
    #  @return  EncoderResponse object
    def start(self, sink):
        try:
            proc = subprocess.Popen(['videoEncoder.sh', 'start'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # TODO: Configure IP

        except Exception:
            self.log.error("Error starting Video Encoder.")
        else:
            #  Save the response variables
            self.state = EncoderResponse.RUNNING
            self.inputActive = True
            self.streamActive = True
            self.log.debug("Video Encoder started.")
        #  Create the response
        response = EncoderResponse()
        response.AppStateT = self.state
        response.inputActive = self.inputActive
        response.streamActive = self.streamActive

        return response

    ## Stops video encoder
    #
    #  @param   self
    #  @return  EncoderResponse object
    def stop(self):
        try:
            proc = subprocess.Popen(['videoEncoder.sh', 'stop'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
        except Exception:
            self.log.error("Error stopping Video Encoder.")
        else:
            #  Save the response variables
            self.state = EncoderResponse.STOPPED
            self.inputActive = False
            self.streamActive = False
            self.log.debug("Video Encoder stopped.")
        # Create the response
        response = EncoderResponse()
        response.AppStateT = self.state
        response.inputActive = self.inputActive
        response.streamActive = self.streamActive

        return response

    ## Reports status
    #
    #  @param   self
    #  @return  EncoderResponse object
    def report(self):
        # Create the response
        response = EncoderResponse()
        response.AppStateT = self.state
        response.inputActive = self.inputActive
        response.streamActive = self.streamActive

        return response