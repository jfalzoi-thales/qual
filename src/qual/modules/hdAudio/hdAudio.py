import os
import subprocess
from time import sleep

from common.gpb.python.HDAudio_pb2 import HDAudioRequest, HDAudioResponse
from common.module.module import Module
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage

## HD Audio class
#
class HDAudio(Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config=None):
        super(HDAudio, self).__init__(config)
        # Add Audio Message handler
        self.addMsgHandler(HDAudioRequest, self.handler)

        ## Audio file path (can be overridden by config)
        self.audioFilePath = "qual/modules/hdAudio/HDAudio"

        # Read config file and update specified instance variables
        self.loadConfig(attributes=('audioFilePath',))

        ## Option to pass to amixer to select audio device
        self.amixerDev = ""
        ## Option to pass to aplay to select audio device
        self.aplayDev = ""

        # Auto-detect what sound device to use
        output = subprocess.check_output("ps ax | grep pulseaudio | grep -v grep || true", shell=True)
        if output != "":
            self.log.info("pulseaudio daemon running; using default audio")
        else:
            dev = subprocess.check_output("aplay -L | fgrep \'sysdefault:CARD=\' | fgrep -v pcsp | head -1 | cut -d \'=\' -f 2 || true", shell=True)
            if dev != "":
                dev = dev.rstrip(" \n\r")
                self.log.info("Using audio device %s" % dev)
                self.amixerDev = "-c \'%s\'" % dev
                self.aplayDev = "-D \'sysdefault:CARD=%s\'" % dev
            else:
                self.log.warning("Unable to determine audio device to use; audio may not play")

        # Add the thread that will play the audio
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
        # Get the HD Audio request
        request = msg.body

        # Response Object
        response = HDAudioResponse()

        # Handle the Request
        if request.requestType == HDAudioRequest.CONNECT:
            if self.state == HDAudioResponse.CONNECTED:
                self.stop()
            # Check if the audio file in source exists
            if not os.path.exists('%s/%s' % (self.audioFilePath, request.source)):
                self.log.error('Missing audio File %s' % (request.source,))
                response = self.report()
            else:
                try:
                    # Check if the volume is in a correct range
                    if request.volume < 0 or request.volume > 100:
                        self.log.warning('Invalid volume range. Changed to 100.')
                        request.volume = 100
                except ValueError:
                    self.log.warning('Wrong message value. Changed to 100.')
                    request.volume = 100
                # Start the module
                response = self.start(request.source, request.volume)
        elif request.requestType == HDAudioRequest.DISCONNECT:
            response = self.stop()
        elif request.requestType == HDAudioRequest.REPORT:
            response = self.report()
        return ThalesZMQMessage(response)

    ## Starts playing audio
    #
    #  @param   self
    #  @param   file    Name of audio file to play
    #  @param   volume  Volume level to set
    #  @return  HDAudioResponse object
    def start(self, file, volume):
        self.file = file
        self.volume = volume
        self.startThread()
        self.state = HDAudioResponse.CONNECTED
        # Create the response
        response = HDAudioResponse()
        response.appState = self.state
        response.source = self.file
        response.volume = self.volume
        return response

    ## Stops playing audio
    #
    #  @param   self
    #  @return  HDAudioResponse object
    def stop(self):
        self._running = False
        proc = subprocess.Popen(['pkill', 'aplay'])
        proc.wait()
        self.stopThread()
        self.state = HDAudioResponse.DISCONNECTED
        self.file = ''
        # Create the response
        response = HDAudioResponse()
        response.appState = self.state
        response.source = self.file
        response.volume = self.volume
        return response

    ## Reports status of audio playback
    #
    #  @param   self
    #  @return  HDAudioResponse object
    def report(self):
        # Create the response
        response = HDAudioResponse()
        response.appState = self.state
        response.source = self.file
        response.volume = self.volume
        return response


    ## Plays the audio file - run in thread
    #
    # @param  self
    def play(self):
        cmd="amixer -q %s sset Master %d%%" % (self.amixerDev, self.volume)
        self.log.debug("Set volume: %s" % cmd)
        rc = subprocess.call(cmd, shell=True)
        if rc != 0:
            self.log.error("Error setting volume")
            sleep(0.5)

        cmd="aplay -q %s %s/%s" % (self.aplayDev, self.audioFilePath, self.file)
        self.log.debug("Play audio: %s" % cmd)
        try:
            subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if "Interrupted system call" in e.output:
                self.log.debug("Audio player stopped")
            else:
                self.log.error("Error playing audio: %s" % e.output)
                sleep(0.5)

        # Make sure thread doesn't spin too fast
        sleep(0.1)
