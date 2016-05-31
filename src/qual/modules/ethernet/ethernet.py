from time import sleep
import subprocess
from common.gpb.python import Ethernet_pb2
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.module import module

## Ethernet Module
#
class Ethernet(module.Module):
    ## Constructor
    #  @param     self
    def __init__(self, config = {}):
        ## initializes parent class
        super(Ethernet, self).__init__({})
        ## adds Ethernet handler to available message handlers
        self.addMsgHandler(Ethernet_pb2.EthernetRequest, self.handler)
        self.chan = ""
        self.server = ""
        ## used to store current iperf subprocess
        self.iperf = None
        self.ethInfo = ""
        self.addThread(self.iperfTracker)

    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param     self
    #  @param     msg       tzmq format message
    #  @return    reply     a ThalesZMQMessage object
    def handler(self, msg):
        self.server = msg.body.remote
        # TODO: Need to handle real channels instead of dummies
        self.chan = msg.body.local
        # TODO: Find out format for response output
        reply = Ethernet_pb2.EthernetResponse()

        if not self._running:
            self.ethInfo = "0 Mbits/sec 0 Retries"

        if msg.body.requestType == Ethernet_pb2.EthernetRequest.RUN:
            reply = self.start()
        elif msg.body.requestType == Ethernet_pb2.EthernetRequest.STOP:
            reply = self.stop()
        elif msg.body.requestType == Ethernet_pb2.EthernetRequest.REPORT:
            reply = self.report()
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        return ThalesZMQMessage(reply)

    def startiperf(self):
        ## 'stdbuf -o L' modifies iperf3 to allow easily accessed line buffered output
        self.iperf = subprocess.Popen(
            ["stdbuf", "-o", "L", "/usr/local/bin/iperf3", "-c", self.server, "-f", "m", "-t", "86400"],
            stdout=subprocess.PIPE, bufsize=1)
        sleep(1)

    def iperfTracker(self):
        ## if iperf3 is already running, skip this.  This ensures that iperf3 restarts after it's 86400 second runtime
        if self.iperf.poll() is not None:
           self.startiperf()

        line = self.iperf.stdout.readline()
        stuff = line.split()

        ## if the 8th field of data is "Mbits/sec" and the number of fields is 11(signifying non-total results), then this is the information we want
        #  EXAMPLE OUTPUT: [  5]   0.00-1.00   sec  23.0 MBytes   193 Mbits/sec    0    211 KBytes
        if len(stuff) == 11 and stuff[7] == "Mbits/sec":
            self.ethInfo = "%s %s %s Retries" % (stuff[6], stuff[7], stuff[8])

    ## Starts iperf3 over a specific channel in order to simulate network traffic
    #
    #  @param     self
    #  @return    self.report() an EthernetResponse object generated by report() function
    def start(self):
        if self.server != None:
            ## kills any iperf3 instances and waits for pkill to complete
            #  this allows for changes in server ip address if iperf3 is already running
            subprocess.Popen(["pkill", "-9", "iperf3"]).communicate()

            if self._running:
                return self.report()

            self.startiperf()
            self.startThread()

        return self.report()

    ## Stops iperf3 over a specific channel
    #
    #  @param     self
    #  @return    self.report() an EthernetResponse object generated by report() function
    def stop(self):
        self._running = False
        subprocess.Popen(["pkill", "-9", "iperf3"]).communicate()
        self.stopThread()

        return self.report()

    ## Reports current iperf3 status
    #
    #  Stores iperf3 information as a GPB object
    #
    #  @param     self
    #  @return    loadResponse  an EthernetResponse object
    def report(self):
        loadResponse = Ethernet_pb2.EthernetResponse()

        if self._running:
            loadResponse.state = Ethernet_pb2.EthernetResponse.RUNNING
        else:
            loadResponse.state = Ethernet_pb2.EthernetResponse.STOPPED

        loadResponse.local = self.chan
        loadResponse.result = self.ethInfo

        return loadResponse

    ## Attempts to kill processes gracefully
    #  @param     self
    def terminate(self):
        self._running = False
        subprocess.Popen(["pkill", "-9", "iperf3"]).communicate()
        self.stopThread()
        sleep(2)