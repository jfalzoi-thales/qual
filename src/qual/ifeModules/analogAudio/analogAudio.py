from Queue import Queue
from subprocess import check_output
from common.gpb.python.AnalogAudio_pb2 import AnalogAudioRequest, AnalogAudioResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.module.module import Module

## AnalogAudio Module Class
class IFEAnalogAudio(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        #  Initializes parent class
        super(IFEAnalogAudio, self).__init__(config)
        ## Dict containing connections, stored by output pin
        self.connections = {}
        ## Dict containing input pins (PA_AUDIN) and ID used for pavaTest.sh
        self.inputs = {"PA_70V_AUDIN_1": 1,
                      "PA_AUDIN_2": 2,
                      "PA_AUDIN_3": 3,
                      "PA_AUDIN_4": 4,
                      "PA_AUDIN_5": 5,
                      "PA_AUDIN_6": 6,
                      "PA_AUDIN_7": 7,
                      "PA_AUDIN_8": 8}
        ## Dict containing output pins (VA_AUDOUT) and ID used for pavaTest.sh
        self.outputs = {"VA_AUDOUT_1": 1,
                        "VA_AUDOUT_2": 2,
                        "VA_AUDOUT_3": 3,
                        "VA_AUDOUT_4": 4,
                        "VA_AUDOUT_5": 5,
                        "VA_AUDOUT_6": 6}
        ## Queue for storing connect and disconnect requests
        self.requests = Queue()
        #  Add handler to available message handlers
        self.addMsgHandler(AnalogAudioRequest, self.handler)
        #  Add thread to handle the request queue
        self.addThread(self.requestQueue)

    ## Handles incoming messages
    #  Receives tzmq request and runs requested process
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  AnalogAudioResponse object
    def handler(self, msg):
        response = AnalogAudioResponse()
        if not self._running: self.startThread()

        if msg.body.sink != "ALL" and msg.body.sink not in self.outputs.keys():
            self.log.warning("Invalid Sink: %s" % msg.body.sink)
        elif msg.body.requestType == AnalogAudioRequest.CONNECT:
            if msg.body.source not in self.inputs.keys():
                self.log.warning("Invalid Source: %s" % msg.body.source)
            else:
                self.requests.put(msg)

            self.report(response, msg.body.sink)
        elif msg.body.requestType == AnalogAudioRequest.DISCONNECT:
            self.requests.put(msg)
            self.report(response, msg.body.sink)
        elif msg.body.requestType == AnalogAudioRequest.REPORT:
            self.report(response, msg.body.sink)
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        return ThalesZMQMessage(response)

    ## Runs pavaTest.sh with specified command and checks output for success
    #  @param   self
    #  @param   cmd         Command to run with pavaTest.sh
    #  @return  success     True if pavaTest.sh was run successfully, else False
    def runPavaTest(self, cmd):
        self.log.info("Running 'pavaTest.sh %s' command." % cmd)
        out = check_output(["pavaTest.sh"] + cmd.split())
        output = out.split()

        if cmd.endswith("-D"):
            if output[len(output) - 1] == "disabled":
                success = True
            else:
                success = False
        else:
            if output[len(output) - 1] == "succeeded":
                success = True
            else:
                success = False

        if not success: self.log.warning("'pavaTest.sh %s' failed to run with output: %s" % (cmd, out))
        return success

    ## Waits for a command to run, then runs commands in the order that they were received
    #  @param   self
    def requestQueue(self):
        msg = self.requests.get(block=True)

        if msg is not "EXIT":
            if msg.body.requestType == AnalogAudioRequest.CONNECT:
                    self.connect(msg.body.source, msg.body.sink)
            else:
                self.disconnect(msg.body.sink)


    ## Connects a specified input to a specified output
    #  @param   self
    #  @param   source      Source input
    #  @param   sink        Sink output
    def connect(self, source, sink):
        self.disconnect(sink)

        if sink == "ALL":
            for output in self.outputs.keys():
                if source not in self.connections.values():
                    #  If the connect commands succeed, add a connection between source input and sink output to self.connections
                    if self.runPavaTest("-c pa -a 239.192.128.%i -k %i" % (self.inputs[source], self.inputs[source])):
                        if self.runPavaTest("-c va -a 239.192.128.%i -k %i" % (self.inputs[source], self.outputs[output])):
                            self.connections[output] = source
                        else:
                            self.runPavaTest("-c pa -k %i -D" % self.inputs[source])
                elif self.runPavaTest("-c va -a 239.192.128.%i -k %i" % (self.inputs[source], self.outputs[output])):
                    self.connections[output] = source
        elif source not in self.connections.values():
            #  If the connect commands succeed, add a connection between source input and sink output to self.connections
            if self.runPavaTest("-c pa -a 239.192.128.%i -k %i" % (self.inputs[source], self.inputs[source])):
                if self.runPavaTest("-c va -a 239.192.128.%i -k %i" % (self.inputs[source], self.outputs[sink])):
                    self.connections[sink] = source
                else:
                    self.runPavaTest("-c pa -k %i -D" % self.inputs[source])
        elif self.runPavaTest("-c va -a 239.192.128.%i -k %i" % (self.inputs[source], self.outputs[sink])):
                self.connections[sink] = source

    ## Disconnects a specified output from its input
    #  @param   self
    #  @param   sink    Sink output to disconnect
    def disconnect(self, sink):
        if sink == "ALL":
            for output in self.outputs.keys():
                if output in self.connections.keys():
                    self.runPavaTest("-c va -k %i -D" % self.outputs[output])
                    source = self.connections.pop(output)

                    if source not in self.connections.values():
                        self.runPavaTest("-c pa -k %i -D" % self.inputs[source])
                else:
                    self.log.debug("Sink output %s not found in self.connections.  Nothing to disconnect." % output)
        else:
            if sink in self.connections.keys():
                self.runPavaTest("-c va -k %i -D" % self.outputs[sink])
                source = self.connections.pop(sink)

                if source not in self.connections.values():
                    self.runPavaTest("-c pa -k %i -D" % self.inputs[source])
            else:
                self.log.debug("Sink output %s not found in self.connections.  Nothing to disconnect." % sink)

    ## Reports connection status
    #  @param   self
    #  @param   response  An AnalogAudioResponse object
    #  @param   sink      Sink output to report on
    def report(self, response, sink):
        if sink == "ALL":
            for output in sorted(self.outputs.keys()):
                loopback = response.loopback.add()
                loopback.sink = output

                if output in self.connections.keys():
                    loopback.source = self.connections[output]
                    loopback.state = AnalogAudioResponse.CONNECTED
                else:
                    loopback.source = ""
                    loopback.state = AnalogAudioResponse.DISCONNECTED
        else:
            loopback = response.loopback.add()
            loopback.sink = sink

            if sink in self.connections.keys():
                loopback.source = self.connections[sink]
                loopback.state = AnalogAudioResponse.CONNECTED
            else:
                loopback.source = ""
                loopback.state = AnalogAudioResponse.DISCONNECTED

    ## Attempts to terminate module gracefully
    #  @param   self
    def terminate(self):
        self._running = False
        self.requests.put("EXIT")
        self.stopThread()
