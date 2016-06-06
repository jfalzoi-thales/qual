import subprocess
from common.gpb.python.Ethernet_pb2 import EthernetRequest, EthernetResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.module import module

## Ethernet Module
class Ethernet(module.Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config = {}):
        super(Ethernet, self).__init__({})
        ## Used to store current iperf subprocess
        self.iperf = None
        ## Indicates which remote iperf3 server should be communicated with
        self.server = ""
        ## Ethernet bandwidth reading from iperf3
        self.bandwidth = 0.0
        ## Cumulative number of retries over iperf3 run
        self.retries = 0
        #  Adds handler to available message handlers
        self.addMsgHandler(EthernetRequest, self.handler)
        #  Enables the use of iperfTraker() as a thread
        self.addThread(self.iperfTracker)

    ## Handles incoming tzmq messages
    #  @param     self
    #  @param     msg   tzmq format message
    #  @return    ThalesZMQMessage object
    def handler(self, msg):
        response = EthernetResponse()
        #  TODO: Need to handle real channels instead of dummies
        response.local = msg.body.local

        #  Resets bandwidth and retries values if not running and before a new run;
        #  this mainly handles the case where a re-RUN command is issued without a STOP
        if not self._running or (msg.body.requestType == EthernetRequest.RUN and msg.body.remote != ""):
            #  We don't want to overwrite the server if an empty server address is sent
            self.server = msg.body.remote
            self.bandwidth = 0.0
            self.retries = 0

        if msg.body.requestType == EthernetRequest.RUN:
            self.start(response)
        elif msg.body.requestType == EthernetRequest.STOP:
            self.stop(response)
        elif msg.body.requestType == EthernetRequest.REPORT:
            self.report(response)
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        return ThalesZMQMessage(response)

    ## Starts iperf3 over a specific channel in order to simulate network traffic
    #  @param   self
    def startiperf(self):
        #  'stdbuf -o L' modifies iperf3 to allow easily accessed line buffered output
        self.iperf = subprocess.Popen(
            ["stdbuf", "-o", "L", "/usr/local/bin/iperf3", "-c", self.server, "-f", "m", "-t", "86400"],
            stdout=subprocess.PIPE, bufsize=1)

    ## Runs in thread to continually gather iperf3 data line by line and restarts iperf3 if process ends
    #  @param   self
    def iperfTracker(self):
        #  If iperf3 is already running, skip this.  This ensures that iperf3 restarts after it's 86400 second runtime
        if self.iperf.poll() is not None:
            self.startiperf()

        line = self.iperf.stdout.readline()
        stuff = line.split()

        #  If the 8th field of data is "Mbits/sec" and the number of fields is 11(signifying non-total results),
        #  then this is the information we want
        #  EXAMPLE OUTPUT: [  5]   0.00-1.00   sec  23.0 MBytes   193 Mbits/sec    0    211 KBytes
        if len(stuff) == 11 and stuff[7] == "Mbits/sec":
            self.bandwidth = float(stuff[6])
            self.retries += int(stuff[8])

    ## Cleans up stray iperf3, calls startiperf(), and reports
    #  @param   self
    #  @param   response    EthernetResponse object
    def start(self, response):
        if self.server != "":
            #  Kills any iperf3 instances and waits for pkill to complete;
            #  this allows for changes in server ip address if iperf3 is already running
            subprocess.Popen(["pkill", "-9", "iperf3"]).communicate()

            if not self._running:
                self.startiperf()
                self.startThread()

        self.report(response)

    ## Stops iperf3 over a specific channel
    #  @param   self
    #  @param   response    EthernetResponse object
    def stop(self, response):
        self._running = False
        subprocess.Popen(["pkill", "-9", "iperf3"]).communicate()
        self.stopThread()
        self.report(response)

    ## Reports current iperf3 status
    #  @param   self
    #  @param   response    EthernetResponse object
    def report(self, response):
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
