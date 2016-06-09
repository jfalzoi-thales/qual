import os
import subprocess

from common.gpb.python.HDAudio_pb2 import HDAudioRequest, HDAudioResponse
from common.module.module import Module
from common.logger.logger import Logger, DEBUG
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from qual.modules.hdAudio.hdAudio_Exception import HDAudioModuleException

## HD Audio class
#
class HDAudio(Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config={}):
        super(HDAudio, self).__init__({})
        ## Log for this module
        self.__log = Logger(name='HD Audio', level=DEBUG)
        ## Add Audio Message handler
        self.addMsgHandler(HDAudioRequest, self.handler)
        ## Add the thread that will play the audio
        self.addThread(self.play)
        ## State of the application
        self.state = HDAudioResponse.DISCONNECTED
        ## Source audio file
        self.file = 'default'
        ## Volume
        self.volume = 100.0

    ## Handles incoming request messages
    #
    # @param  self
    # @param  msg       TZMQ format message
    # @return reply     a ThalesZMQMessage object containing the response message
    def handler(self, msg):
        ## Get the HD Audio request
        request = msg.body

        ## Response Object
        response = HDAudioResponse()

        ## Handle the Request
        if request.requestType == HDAudioRequest.CONNECT:
            if self.state == HDAudioResponse.CONNECTED:
                self.stop()
            ## Check if the audio file in source exists
            if not os.path.exists('../modules/hdAudio/%s' % (request.source,)):
                raise HDAudioModuleException(msg='Missing audio File %s' % (request.source,))
            try:
                ## Check if the volume is in a correct range
                if request.volume < 0 or request.volume > 100:
                    self.__log.warning('Invalid volume range. Changed to 100.')
                    request.volume = 100
            except ValueError:
                self.__log.warning('Wrong message value. Changed to 100.')
                request.volume = 100
            ## Start the module
            response = self.start(request.source, request.volume)
        elif request.requestType == HDAudioRequest.DISCONNECT:
            response = self.stop()
        elif request.requestType == HDAudioRequest.REPORT:
            response = self.report()
        return ThalesZMQMessage(response)

    ## Starts the module
    #
    #  @param   self
    def start(self, file, volume):
        self.file = file
        self.volume = volume
        self.startThread()
        self.state = HDAudioResponse.CONNECTED
        ## Create the response
        response = HDAudioResponse()
        response.appState = self.state
        response.source = self.file
        response.volume = self.volume
        return response

    ## Stops the module
    #
    #  @param   self
    def stop(self):
        self._running = False
        proc = subprocess.Popen(['pkill', 'aplay'])
        proc.wait()
        self.stopThread()
        self.state = HDAudioResponse.DISCONNECTED
        ## Create the response
        response = HDAudioResponse()
        response.appState = self.state
        response.source = self.file
        response.volume = self.volume
        return response

    ## Reports the module
    #
    #  @param   self
    def report(self):
        ## Create the response
        response = HDAudioResponse()
        response.appState = self.state
        response.source = self.file
        response.volume = self.volume
        return response


    ## Plays the audio file
    #
    # @param  self
    def play(self):
        proc = subprocess.Popen(['amixer', 'sset', 'Master', str(self.volume)+'%'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        proc = subprocess.Popen(['aplay', '-V', 'stereo', '../modules/hdAudio/%s' % (self.file,)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
