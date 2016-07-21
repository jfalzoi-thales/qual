import subprocess
import collections
from common.gpb.python.ARINC485_pb2 import ARINC485Request, ARINC485Response
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.module.module import Module

## ARINC485 Module Class
class ARINC485(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        #  Initializes parent class
        super(ARINC485, self).__init__(config)
        ## Baudrate for demo_serial485, which is one of 2400, 9600, or 115200
        self.baudrate = 9600
        ## Parity for demo_serial485, which is one of N, O, or E
        self.parity = 'N'
        ## Stopbits for demo_serial485, which is one of 1 or 2
        self.stopbits = 1
        ## Byesize (Databits) for demo_serial485, which is one of 7 or 8
        self.bytesize = 8
        #  Use config file values if available
        self.loadConfig(attributes=('baudrate', 'parity', 'stopbits', 'bytesize'))
        ## Named tuple type to store port statistics
        self.stats = collections.namedtuple("stats", "missed received")
        ## Dict containing port statistics
        self.ports = {"Slave1":self.stats(0, 0),
                      "Slave2":self.stats(0, 0),
                      "Slave3":self.stats(0, 0),
                      "Slave4":self.stats(0, 0),
                      "Slave5":self.stats(0, 0)}
        ## Current instance of demo_serial485
        self.demo = None
        #  Add thread to run demo_serial485
        self.addThread(self.demoSerialTracker)
        #  Add handler to available message handlers
        self.addMsgHandler(ARINC485Request, self.handler)

    ## Handles incoming messages
    #  Receives tzmq request and runs requested process
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  ARINC485Response object
    def handler(self, msg):
        response = ARINC485Response()

        if msg.body.requestType == ARINC485Request.RUN:
            self.start(response)
        elif msg.body.requestType == ARINC485Request.STOP:
            self.stop(response)
        elif msg.body.requestType == ARINC485Request.REPORT:
            self.report(response)
        else:
            self.log.error("Unexpected Request Type %d" %(msg.body.requestType))

        return ThalesZMQMessage(response)

    ## Runs demo_serial485 to
    #  @param   self
    def startDemoSerial(self):
        self.demo = subprocess.Popen(
            ["demo_serial485", "ar485LoopbackTest2", str(self.baudrate), str(self.bytesize), str(self.stopbits),
             self.parity, "1"], stdout=subprocess.PIPE, bufsize=1).communicate()

    ## Runs in thread to continually run and gather demo_serial485 data
    #  @param   self
    def demoSerialTracker(self):
        self.startDemoSerial()
        lines = self.demo.readlines()

        for port in self.ports.keys():
            for line in lines:
                fields = line.split()

                #  Check that current line is not header and that the port is the current port
                if len(fields) > 3 and fields[0] == "Master-%s" % port:
                    if fields[2] == "0":
                        self.ports[port].missed += 1
                    elif fields[2] == "1":
                        self.ports[port].received += 1
                    else:
                        self.log.error("Unexpected output: %s" % line)





    ## Starts lookbusy process to mimic specific CPU loads
    #  Uses console commands to remove previous lookbusy instances, starts a new CPU load, and reports current CPU load
    #  @param   self
    #  @param   response    A ARINC485Response object generated by report() function
    #  @param   level       Integer to specify percentage of CPU load [DEFAULT = 80]
    def start(self, response):
        self.report(response)

    ## Stops CPU load from lookbusy instances
    #  Uses console commands to remove lookbusy instances and reports current CPU load
    #  @param   self
    #  @param   response  A ARINC485Response object generated by report() function
    def stop(self, response):
        self.report(response)

    ## Reports current CPU load information provided by linux
    #  Polls CPULoader thread for CPU load information and creates ARINC485Response object
    #  @param   self
    #  @param   response  A ARINC485Response object
    def report(self, response):


    ## Attempts to terminate module gracefully
    #  @param   self
    def terminate(self):
