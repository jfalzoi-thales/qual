import subprocess
import collections
from nms.common.portresolver.portResolver import resolvePort, portNames
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from nms.guest.pb2.nms_guest_api_pb2 import PortInfoReq, PortInfoResp


## PortInfo Module
class PortInfo(Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config=None):
        super(PortInfo, self).__init__(config)
        ## Named tuple for storing key functions and parsing fields
        self.keyInfo = collections.namedtuple("keyInfo", "func field")
        ## Dict containing possible keys and their functions for internal ports
        self.insidePortFuncs = {"shutdown":           self.keyInfo(self.runIpLinkShow, 8),
                                  "speed":              self.keyInfo(self.getEthdata, "Speed"),
                                  "configured_speed":   self.keyInfo(self.getEthdata, "Auto-negotiation"),
                                  "flow_control":       self.keyInfo(self.runEthtoola, 0),
                                  "MTU":                self.keyInfo(self.runIpLinkShow, 4),
                                  "link":               self.keyInfo(self.getEthdata, "Link detected"),
                                  "vlan_id":            self.keyInfo(self.runFakeVlan, 1337),
                                  "BPDU_state":         self.keyInfo(self.unsupported, 0)}
        ## Dict containing possible keys and their functions for external ports
        self.outsidePortFuncs = {"shutdown":           self.keyInfo(self.tempFunc, 0),
                                  "speed":              self.keyInfo(self.tempFunc, 0),
                                  "configured_speed":   self.keyInfo(self.tempFunc, 0),
                                  "flow_control":       self.keyInfo(self.tempFunc, 0),
                                  "MTU":                self.keyInfo(self.tempFunc, 0),
                                  "link":               self.keyInfo(self.tempFunc, 0),
                                  "vlan_id":            self.keyInfo(self.tempFunc, 0),
                                  "BPDU_state":         self.keyInfo(self.tempFunc, 0)}
        ## Dict for storing relevant output from Ethtool calls
        self.ethCache = {}
        ## Dict for storing relevant output from IpLinkShow calls
        self.ipLinkCache = {}
        #  Adds handler to available message handlers
        self.addMsgHandler(PortInfoReq, self.handler)

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def handler(self, msg):
        response = PortInfoResp()

        if msg.body != None:
            for key in msg.body.portInfoKey:
                keyParts = key.split(".")

                if self.checkKey(response, keyParts):
                    if "*" in keyParts:
                        self.wild(response, keyParts)
                    else:
                        self.ethCache = {}
                        name = '.'.join(keyParts[:-1])
                        port = resolvePort(name)

                        if port[1]:
                            self.outside(response, name, keyParts[-1], port[0])
                        else:
                            self.inside(response, name, keyParts[-1], port[0])
        else:
            self.wild(response, ["*"])

        return ThalesZMQMessage(response)

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def checkKey(self, response, keyParts):
        errcode = 1004

        if keyParts[-1] in self.insidePortFuncs.keys() + self.outsidePortFuncs.keys() + ["*"]:
            if resolvePort('.'.join(keyParts[:-1])) != None:
                return True
            elif keyParts[0] == "*":
                return True
            else:
                errcode = 1003

        self.log.warning("Incorrect key format: %s" % '.'.join(keyParts))
        response.add()
        response.values.keyValue.key = '.'.join(keyParts)
        self.error(response, errcode)

        return False

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def wild(self, response, keyParts):
        if keyParts[0] == "*":
            for name in portNames:
                self.ethCache = {}
                port = resolvePort(name)

                if port[1]:
                    if keyParts[-1] == "*":
                        for stat in self.outsidePortFuncs:
                            self.outside(response, name, stat, port[0])
                    else:
                        self.outside(response, name, keyParts[-1], port[0])
                else:
                    if keyParts[-1] == "*":
                        for stat in self.insidePortFuncs:
                            self.inside(response, name, stat, port[0])
                    else:
                        self.inside(response, name, keyParts[-1], port[0])
        else:
            self.ethCache = {}
            name = '.'.join(keyParts[:-1])
            port = resolvePort(name)

            if port[1]:
                for stat in self.outsidePortFuncs:
                    self.outside(response, name, stat, port[0])
            else:
                for stat in self.insidePortFuncs:
                    self.inside(response, name, stat, port[0])

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def inside(self, response, name, stat, port):
        response.add()
        response.values.keyValue.key = '.'.join([name, stat])
        call = self.insidePortFuncs[stat]
        call.func(response, port, call.field)

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def outside(self, response, name, stat, port):
        response.add()
        response.values.keyValue.key = '.'.join([name, stat])
        call = self.outsidePortFuncs[stat]
        call.func(response, port, call.field)

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def tempFunc(self, response, keyParts, port, field):
        print "Called placeholder function! \o/"
        response.values.success = True
        response.values.keyValue.value = "YAY SUCCESS"

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def runIpLinkShow(self, response, port, field):
        try:
            #  The logic at the end removes unnecessary info from the front and splits by line
            out = subprocess.check_output(["ip", "link", "show", port]).split('> ')[-1].split('\n')
            data =[]
            count = 0

            for line in out:
                data += line.strip().split()

            while count < len(data):
                self.ipLinkCache[data[count]] = data[count + 1]
                count += 2
        except:
            self.ipLinkCache = {}

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def runEthtool(self, port):
        try:
            out = subprocess.check_output(["ethtool", port])

            for line in out.split('\n'):
                if ":" in line:
                    data = line.split(':')
                    self.ethCache[data[0].strip()] = data[1].strip()
        except:
            self.ethCache = {}

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def getEthdata(self, response, port, field):
        portSpeed = {"10" : "FORCE10MODE",
                     "100" : "FORCE100MODE",
                     "1000" : "FORCE1GMODE",
                     "2500" : "FORCE2G5MODE",
                     "5000" : "FORCE5GMODE",
                     "10000" : "FORCE10GMODE",
                     "12000" : "FORCE12GMODE"}

        if not self.ethCache:
            self.runEthtool(port)

        if field in self.ethCache:
            response.values.success = True

            if field == "Speed":
                speed = portSpeed[self.ethCache["Speed"].rstrip('Mb/s')]
                duplex = "FDX" if self.ethCache["Duplex"] == "Full" else "HDX"
                response.values.keyValue.value = speed + duplex
            elif field == "Auto-negotiation":
                if self.ethCache["Auto-negotiation"] == "on":
                    response.values.keyValue.value = "AUTONEGMODE"
                else:
                    speed = portSpeed[self.ethCache["Speed"].rstrip('Mb/s')]
                    duplex = "FDX" if self.ethCache["Duplex"] == "Full" else "HDX"
                    response.values.keyValue.value = speed + duplex
            else:
                response.values.keyValue.value = self.ethCache[field]
        else:
            self.error(response, 1005)

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def runEthtoola(self, response, port, field):
        try:
            out = subprocess.check_output(["ethtool", "-a", port])
            response.values.success = True
            response.values.keyValue.value = out.split('\n')[field]
        except:
            self.error(response, 1005)

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def runFakeVlan(self, response, port, field):
            response.values.success = True
            response.values.keyValue.value = "YAY SUCCESS! \o/"

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def unsupported(self, response, port, field):
        self.error(response, 1001)

    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def error(self, response, code):
        response.success = False
        response.values.keyValue.value = ""
        response.values.error.error_code = code

        if code == 1001:
            response.values.error.error_description = "Port is not supported in this setup"
        elif code == 1002:
            response.values.error.error_description = "Port is not active"
        elif code == 1003:
            response.values.error.error_description = "Port name does not exist in this setup"
        elif code == 1004:
            response.values.error.error_description = "Invalid Message Received"
        elif code == 1005:
            response.values.error.error_description = "Error Processing Message"
        else:
            response.values.error.error_description = "Unrecognized Error Code"