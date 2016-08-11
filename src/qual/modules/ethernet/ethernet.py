import subprocess
import threading
from time import sleep
import netifaces
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
        ## Ethernet device to use for local port ENET_8
        self.port8Device = "eno1"
        self.loadConfig(attributes=('bandwidthSpeed', 'port8Device'))
        ## Dict of connections; key is local port, value is a ConnectionInfo object
        self.connections = {}
        ## Lock for access to connections dict
        self.connectionsLock = threading.Lock()
        ## Default server to connect to if not specified in request
        self.defaultServer = ""
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
        # TODO: Validate local port
        response.local = msg.body.local

        if msg.body.requestType == EthernetRequest.RUN:
            self.start(msg.body, response)
        elif msg.body.requestType == EthernetRequest.STOP:
            self.stop(msg.body, response)
        elif msg.body.requestType == EthernetRequest.REPORT:
            self.report(msg.body, response)
        else:
            self.log.error("Unexpected Request Type %d" % msg.body.requestType)

        return ThalesZMQMessage(response)

    ## Starts iperf3 over a specific channel in order to simulate network traffic
    #  @param   self
    #  @param   connection ConnectionInfo object for this connection
    def startiperf(self, connection):
        #  'stdbuf -o L' modifies iperf3 to allow easily accessed line buffered output
        cmd = ["stdbuf", "-o", "L", "iperf3", "-c", connection.server, "-b", "%sM" % str(self.bandwidthSpeed), "-f", "m", "-t", "86400"]
        # Port ENET_8 is connected directly to interface eno1 on the MPS so
        # if ENET_8 is specified, bind to the address of that port if possible.
        if connection.localPort == "ENET_8" and self.port8Device in netifaces.interfaces():
            ifaddrs = netifaces.ifaddresses(self.port8Device)
            if netifaces.AF_INET in ifaddrs:
                for ipcfg in ifaddrs[netifaces.AF_INET]:
                    if "addr" in ipcfg:
                        cmd += ["-B", ipcfg["addr"]]
                        break
            else:
                self.log.warning("Interface %s does not have IP address", self.port8Device)
        else:
            self.log.warning("Interface %s not present", self.port8Device)

        self.log.info("Starting: %s" % " ".join(cmd))
        connection.iperf = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1)

    ## Terminates a running iperf on a connection
    #  @param   self
    #  @param   connection ConnectionInfo object for this connection
    def stopiperf(self, connection):
        if connection.iperf is not None:
            connection.iperf.terminate()
            connection.iperf.wait()
            connection.iperf = None

    ## Runs in thread to continually gather iperf3 data line by line and restarts iperf3 if process ends
    #  @param   self
    def iperfTracker(self):
        #self.log.info("top of iperfTracker")
        #  Make a shallow copy of connections to reduce locking in background thread
        self.connectionsLock.acquire()
        connectionsCopy = dict.copy(self.connections)
        self.connectionsLock.release()

        for connection in connectionsCopy.values():
            iperf = connection.iperf

            if iperf is not None:
                #  If iperf3 has exited, restart it (iperf3 has a maximum runtime before it exits)
                if connection.iperf.poll() is not None:
                    self.log.debug("iperf on port %s ended; restarting" % connection.localPort)

                    if connection.iperf.returncode != 0:
                        connection.iperf = None
                        sleep(.5)

                    self.startiperf(connection)

                line = connection.iperf.stdout.readline()
                self.log.debug("Port %s: %s" % (connection.localPort, line))
                stuff = line.split()

                #  If the 8th field of data is "Mbits/sec" and the number of fields is 11(signifying non-total results),
                #  then this is the information we want
                #  EXAMPLE OUTPUT: [  5]   0.00-1.00   sec  23.0 MBytes   193 Mbits/sec    0    211 KBytes
                if len(stuff) == 11 and stuff[7] == "Mbits/sec":
                    connection.bandwidth = float(stuff[6])
                    connection.retries += int(stuff[8])

        #  Without this delay, iperfTracker is capable of re-acquiring lock before other blocked functions
        sleep(.001)

    ## Starts or restarts iperf3 on the specified channel
    #  @param   self
    #  @param   response    EthernetResponse object
    def start(self, request, response):
        # If a remote server was provided, update our default server
        if request.remote != "":
            self.defaultServer = request.remote

        # If no remote server was provided and we don't have a default, respond without doing anything
        if request.remote == "" and self.defaultServer == "":
            self.log.warning("Attempt to start streaming with no server specified")
            self.report(request, response)
            return

        localPort = str(request.local)
        remoteServer = request.remote if request.remote != "" else self.defaultServer

        # If this connection is not active, add it to our connection list, else get the connection object
        if localPort not in self.connections:
            self.log.info("Starting streaming on port %s to %s" % (localPort, remoteServer))
            connection = ConnectionInfo(localPort)
            self.connectionsLock.acquire()
            self.connections[localPort] = connection
            self.connectionsLock.release()
        else:
            self.log.info("Restarting streaming on port %s to %s" % (localPort, remoteServer))
            connection = self.connections[localPort]
            # Stop streaming and reset stats
            self.stopiperf(connection)
            connection.bandwidth = 0.0
            connection.retries = 0

        # TODO: set up switch port routing

        # Start streaming to the specified remote server
        connection.server = remoteServer
        self.startiperf(connection)

        if not self._running:
            self.log.debug("Starting iperfTracker")
            self.startThread()

        self.report(request, response)

    ## Stops iperf3 on the specified channel
    #  @param   self
    #  @param   response    EthernetResponse object
    def stop(self, request, response):
        localPort = str(request.local)
        # Run the report before actually stopping to get the final bandwidth and retries values
        self.report(request, response)
        response.state = EthernetResponse.STOPPED

        # Now stop the iperf and remove from our connections list
        if localPort in self.connections:
            self.connectionsLock.acquire()
            connection = self.connections.pop(localPort)
            self.connectionsLock.release()
            self.log.info("Stopping streaming on port %s to %s" % (localPort, connection.server))
            self.stopiperf(connection)

        # If no connections active, shut down the iperfTracker thread
        if len(self.connections) == 0 and self._running:
            self.log.debug("Stopping iperfTracker")
            self._running = False
            self.stopThread()

    ## Reports current iperf3 status on the specified channel
    #  @param   self
    #  @param   response    EthernetResponse object
    def report(self, request, response):
        localPort = str(request.local)

        if localPort in self.connections:
            response.state = EthernetResponse.RUNNING
            response.bandwidth = self.connections[localPort].bandwidth
            response.retries = self.connections[localPort].retries
        else:
            response.state = EthernetResponse.STOPPED
            response.bandwidth = 0.0
            response.retries = 0

    ## Attempts to stop instance gracefully
    #  @param   self
    def terminate(self):
        if self._running:
            self._running = False
            self.connectionsLock.acquire()
            for connection in self.connections.values():
                self.log.info("Stopping streaming on port %s to %s" % (connection.localPort, connection.server))
                self.stopiperf(connection)
            self.connectionsLock.release()
            self.stopThread()
