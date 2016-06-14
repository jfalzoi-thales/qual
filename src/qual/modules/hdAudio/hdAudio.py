import os
import subprocess
from time import sleep

from common.gpb.python.HDAudio_pb2 import HDAudioRequest, HDAudioResponse
from common.module.module import Module
from common.logger.logger import Logger, DEBUG
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage

## HD Audio class
#
class HDAudio(Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config={}):
        super(HDAudio, self).__init__({})
        ## Add Audio Message handler
        self.addMsgHandler(HDAudioRequest, self.handler)
        ## Add the thread that will play the audio
        self.addThread(self.play)
        ## State of the application
        self.state = HDAudioResponse.DISCONNECTED
        ## Source audio file
        self.file = ''
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
            ## TODO: Make this path configurable
            if not os.path.exists('qual/modules/hdAudio/HDAudio/%s' % (request.source,)):
                self.log.error('Missing audio File %s' % (request.source,))
                response = self.report()
            else:
                try:
                    ## Check if the volume is in a correct range
                    if request.volume < 0 or request.volume > 100:
                        self.log.warning('Invalid volume range. Changed to 100.')
                        request.volume = 100
                except ValueError:
                    self.log.warning('Wrong message value. Changed to 100.')
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
        self.file = ''
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
        cmd=['amixer', '-q', 'sset', 'Master', str(self.volume)+'%']
        self.log.debug("Set volume: %s" % " ".join(cmd))
        rc = subprocess.call(cmd)
        if rc != 0:
            self.log.error("Error setting volume")
            sleep(0.5)

        cmd=['aplay', '-q', 'qual/modules/hdAudio/HDAudio/%s' % (self.file,)]
        self.log.debug("Play audio: %s" % " ".join(cmd))
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if "Interrupted system call" in e.output:
                self.log.debug("Audio player stopped")
            else:
                self.log.error("Error playing audio: %s" % e.output)
                sleep(0.5)

        # Make sure thread doesn't spin too fast
        sleep(0.1)
