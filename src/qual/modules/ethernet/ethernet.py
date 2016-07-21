import subprocess
import os
from common.gpb.python.Ethernet_pb2 import EthernetRequest, EthernetResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.module.module import Module, ModuleException

## Ethernet Module Exception Class
class EthernetModuleException(ModuleException):
    ## Constructor
    #  @param     self
    #  @param     msg  Message text associated with this exception
    def __init__(self, msg):
        super(EthernetModuleException, self).__init__()
        ## Message text associated with this exception
        self.msg = msg

## Connection info container class
class ConnectionInfo(object):
    ## Constructor
    #  @param     self
    #  @param     outputPin  Output pin name
    def __init__(self, localPort):
        super(ConnectionInfo, self).__init__()
        ## Name of local port to route traffic to
        self.localPort = localPort
        ## IP address of remote iperf3 server to communicate with
        self.server = ""
        ## Used to store iperf subprocess
        self.iperf = None
        ## Network bandwidth reading from iperf3
        self.bandwidth = 0.0
        ## Cumulative number of retries over iperf3 run
        self.retries = 0


## Ethernet Module
class Ethernet(Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config = None):
        super(Ethernet, self).__init__(config)
        ## Speed at which to send traffic in Mbits per second (0 for unlimited)
        self.bandwidthSpeed = 0
        self.loadConfig(attributes=('bandwidthSpeed',))
        ## Dict of connections; key is local port, value is a ConnectionInfo object
        self.connections = {}
        #  Enables the use of iperfTraker() as a thread
        self.addThread(self.iperfTracker)
        #  Adds handler to available message handlers
        self.addMsgHandler(EthernetRequest, self.handler)

    ## Handles incoming tzmq messages
    #  @param     self
    #  @param     msg   tzmq format message
    #  @return    ThalesZMQMessage object
    def handler(self, msg):
        response = EthernetResponse()
        response.local = msg.body.local

        #  Resets bandwidth and retries values if not running and before a new run;
        #  this mainly handles the case where a re-RUN command is issued without a STOP
        if not self._running or (msg.body.requestType == EthernetRequest.RUN and msg.body.remote != ""):
            #  We don't want to overwrite the server if an empty server address is sent
            self.server = msg.body.remote

        if msg.body.requestType == EthernetRequest.RUN:
            self.start(msg.body, response)
        elif msg.body.requestType == EthernetRequest.STOP:
            self.stop(msg.body, response)
        elif msg.body.requestType == EthernetRequest.REPORT:
            self.report(msg.body, response)
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        return ThalesZMQMessage(response)

    ## Starts iperf3 over a specific channel in order to simulate network traffic
    #  @param   self
    def startiperf(self, connection):
        #  'stdbuf -o L' modifies iperf3 to allow easily accessed line buffered output
        connection.iperf = subprocess.Popen(
            ["stdbuf", "-o", "L", "iperf3", "-c", connection.server, "-b", "%sM" % str(self.bandwidthSpeed), "-f", "m", "-t", "86400"],
            stdout=subprocess.PIPE, bufsize=1)

    ## Runs in thread to continually gather iperf3 data line by line and restarts iperf3 if process ends
    #  @param   self
    def iperfTracker(self):
        # TODO: add locking
        for connection in self.connections.values():
            #  If iperf3 is already running, skip this.  This ensures that iperf3 restarts after its 86400 second runtime
            if connection.iperf.poll() is not None:
                self.startiperf(connection)

            line = connection.iperf.stdout.readline()
            stuff = line.split()

            #  If the 8th field of data is "Mbits/sec" and the number of fields is 11(signifying non-total results),
            #  then this is the information we want
            #  EXAMPLE OUTPUT: [  5]   0.00-1.00   sec  23.0 MBytes   193 Mbits/sec    0    211 KBytes
            if len(stuff) == 11 and stuff[7] == "Mbits/sec":
                connection.bandwidth = float(stuff[6])
                connection.retries += int(stuff[8])

    ## Creates a new connection, calls startiperf(), and reports
    #  @param   self
    #  @param   response    EthernetResponse object
    def start(self, request, response):
        if str(request.local) not in self.connections:
            connection = ConnectionInfo(str(request.local))
            connection.remote = request.remote
            self.connections[str(request.local)] = connection
            self.startiperf(connection)
            if not self._running:
                self.startThread()
        else:
            connection = self.connections[str(request.local)]
            if request.server != connection.server:
                # Remote connection has changed; stop, then restart to new 

        self.report(request, response)

    ## Stops iperf3 over a specific channel
    #  @param   self
    #  @param   response    EthernetResponse object
    def stop(self, request, response):
        #self._running = False
        #subprocess.Popen(["pkill", "-9", "iperf3"]).communicate()
        #self.stopThread()
        self.report(request, response)

    ## Reports current iperf3 status
    #  @param   self
    #  @param   response    EthernetResponse object
    def report(self, request, response):
        if self._running:
            response.state = EthernetResponse.RUNNING
        else:
            response.state = EthernetResponse.STOPPED

        response.bandwidth = self.bandwidth
        response.retries = self.retries

    ## Attempts to stop instance gracefully
    #  @param   self
    def terminate(self):
        self._running = False
        subprocess.Popen(["pkill", "-9", "iperf3"]).communicate()
        self.stopThread()