import collections
from subprocess import check_output, CalledProcessError

from nms.common.portresolver.portResolver import resolvePort, portNames
from nms.guest.pb2.nms_guest_api_pb2 import *
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.vtss.vtss import Vtss

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
        self.insidePortFuncs = {"shutdown":             self.keyInfo(self.getIpLinkData, "state"),
                                "speed":                self.keyInfo(self.getEthData, "Speed"),
                                "configured_speed":     self.keyInfo(self.getEthData, "Auto-negotiation"),
                                "flow_control":         self.keyInfo(self.runEthtoola, 0),
                                "MTU":                  self.keyInfo(self.getIpLinkData, "mtu"),
                                "link":                 self.keyInfo(self.getEthData, "Link detected"),
                                "vlan_id":              self.keyInfo(self.tempFunc, 0),
                                "BPDU_state":           self.keyInfo(self.unsupported, 0)}
        ## Dict containing possible keys and their functions for external ports
        self.outsidePortFuncs = {"shutdown":            self.keyInfo(self.getPortConfigInfo, "Shutdown"),
                                 "speed":               self.keyInfo(self.getPortStatusInfo, "Speed"),
                                 "configured_speed":    self.keyInfo(self.getPortConfigInfo, "Speed"),
                                 "flow_control":        self.keyInfo(self.getPortConfigInfo, "FC"),
                                 "MTU":                 self.keyInfo(self.getPortConfigInfo, "MTU"),
                                 "link":                self.keyInfo(self.getPortStatusInfo, "Link"),
                                 "vlan_id":             self.keyInfo(self.getVlan          , "TrunkVlans"),
                                 "BPDU_state":          self.keyInfo(self.tempFunc         ,  0)}
        ## Dict containing error codes and descriptions defined by ICD
        self.errors = {1001: "Port is not supported in this setup",
                       1002: "Port is not active",
                       1003: "Port name does not exist in this setup",
                       1004: "Invalid Message Received",
                       1005: "Error Processing Message"}
        ## Dict for storing relevant output from Ethtool calls
        self.ethCache = {}
        ## Dict for storing relevant output from IpLinkShow calls
        self.ipLinkCache = {}
        ## Dict for storing relevant output from VTSS RPC
        self.configCache = {}
        ## Dict for storing relevant output from VTSS RPC
        self.statusCache = {}
        ## IP address of the device
        self.switchAddress = "10.10.41.159"
        # Load config file
        self.loadConfig(attributes=('switchAddress'))
        ## Object to call the RPC
        self.vtss = Vtss(switchIP=self.switchAddress)
        #  Adds handler to available message handlers
        self.addMsgHandler(PortInfoReq, self.handler)

    ## Handles incoming messages
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  ThalesZMQMessage object
    def handler(self, msg):
        response = PortInfoResp()

        if msg.body != None:
            for key in msg.body.portInfoKey:
                keyParts = key.rsplit('.', 1)

                if "*" in keyParts:
                    self.wild(response, key, keyParts)
                elif keyParts[-1] in self.insidePortFuncs.keys() + self.outsidePortFuncs.keys():
                    port = resolvePort(keyParts[0])

                    if port:
                        self.ethCache = {}
                        self.ipLinkCache = {}
                        self.configCache = {}
                        self.statusCache = {}

                        if port[1]:
                            self.callFunc(response, key, keyParts[-1], port[0])
                        else:
                            self.callFunc(response, key, keyParts[-1], port[0], False)
                    else:
                        self.log.warning("Unknown key: %s" % key)
                        self.addResp(response, key=key, errCode=1003)
                else:
                    self.log.warning("Invalid key: %s" % key)
                    self.addResp(response, key=key, errCode=1004)
        else:
            self.wild(response, "*", ["*"])

        return ThalesZMQMessage(response)

    ## Adds another set of values to the repeated values response field
    #  @param   self
    #  @param   response    A PortInfoResp object
    #  @param   success     Success flag to be added to response, default False
    #  @param   key         Key to be added to response, default empty
    #  @param   value       Value of key to be added to response, default empty
    #  @param   errCode     Error code for optional ErrorMessage field
    def addResp(self, response, success=False, key="", value="",  errCode=None):
        respVal = response.values.add()
        respVal.success = success
        respVal.keyValue.key = key
        respVal.keyValue.value = value

        if errCode:
            respVal.error.error_code = errCode
            respVal.error.error_description = self.errors[errCode] if errCode in self.errors else "Unrecognized Error Code"

    ## Handles wildcards (*) in requested keys
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   keyParts  Key split on last separator
    def wild(self, response, key, keyParts):
        self.ethCache = {}
        self.ipLinkCache = {}
        self.configCache = {}
        self.statusCache = {}

        if keyParts[0] == "*":
            for name in portNames:
                port = resolvePort(name)

                if port[1]:
                    if keyParts[-1] == "*":
                        for stat in self.outsidePortFuncs:
                            self.callFunc(response, name + '.' + stat, stat, port[0])
                    else:
                        self.callFunc(response, name + '.' + keyParts[-1], keyParts[-1], port[0])
                else:
                    if keyParts[-1] == "*":
                        for stat in self.insidePortFuncs:
                            self.callFunc(response, name + '.' + stat, stat, port[0], False)
                    else:
                        self.callFunc(response, name + '.' + keyParts[-1], keyParts[-1], port[0], False)
        else:
            name = keyParts[0]
            port = resolvePort(name)

            if port[1]:
                for stat in self.outsidePortFuncs:
                    self.callFunc(response, name + '.' + stat, stat, port[0])
            else:
                for stat in self.insidePortFuncs:
                    self.callFunc(response, name + '.' + stat, stat, port[0], False)

    ## Calls appropriate function with specified parameters
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   stat      Requested statistic
    #  @param   port      Port name for function calls
    #  @param   external  True if port is external, False if port is internal
    def callFunc(self, response, key, stat, port, external=True):
        if external:
            call = self.outsidePortFuncs[stat]
        else:
            call = self.insidePortFuncs[stat]

        call.func(response, key, port, call.field)

    ## Temporary function for unimplemented key requests
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def tempFunc(self, response, key, port, field):
        self.log.info("Called placeholder function! \o/")
        self.addResp(response, True, key, "YAY SUCCESS")

    ## Populates ipLinkCache with values
    #  @param   self
    #  @param   port    Port name for function calls
    def runIpLinkShow(self, port):
        try:
            data = []
            count = 0
            #  The logic at the end removes unnecessary info from the front and splits by line
            out = check_output(["ip", "link", "show", port]).split('> ')[-1].split('\n')

            for line in out:
                data += line.strip().split()

            while (len(data) - count) > 1:
                self.ipLinkCache[data[count]] = data[count + 1]
                count += 2
        except CalledProcessError as err:
            self.log.error("Problem running command: %s" % err.cmd)
            self.ipLinkCache = {}

    ## Handles external key requests with data stored in ipLinkCache
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def getIpLinkData(self, response, key, port, field):
        value = None

        if not self.ipLinkCache:
            self.runIpLinkShow(port)

        if field in self.ipLinkCache:
            if field == "state":
                value = "POWERED" if self.ipLinkCache[field] == "UP" else "SHUTDOWN"
            elif field == "mtu":
                value = bytes(self.ipLinkCache[field])

        if value:
            self.addResp(response, True, key, value)
        else:
            self.log.error("Unable to obtain value from ipLink cache.")
            self.addResp(response, key=key, errCode=1005)

    ## Populates ethCache with values
    #  @param   self
    #  @param   port    Port name for function calls
    def runEthtool(self, port):
        try:
            out = check_output(["ethtool", port])

            for line in out.split('\n'):
                if ":" in line:
                    data = line.split(':')
                    self.ethCache[data[0].strip()] = data[1].strip()
        except CalledProcessError as err:
            self.log.error("Problem running command: %s" % err.cmd)
            self.ethCache = {}

    ## Handles external key requests with data stored in ethCache
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def getEthData(self, response, key, port, field):
        portSpeed = {"10" : "FORCE10MODE",
                     "100" : "FORCE100MODE",
                     "1000" : "FORCE1GMODE",
                     "2500" : "FORCE2G5MODE",
                     "5000" : "FORCE5GMODE",
                     "10000" : "FORCE10GMODE",
                     "12000" : "FORCE12GMODE"}
        value = None

        if not self.ethCache:
            self.runEthtool(port)

        if field in self.ethCache:
            if field == "Speed" or [field == "Auto-negotiation" and self.ethCache[field] != "on"]:
                speed = portSpeed[self.ethCache["Speed"].rstrip('Mb/s')]
                duplex = "FDX" if self.ethCache["Duplex"] == "Full" else "HDX"
                value = speed + duplex
            elif field == "Auto-negotiation" and self.ethCache["Auto-negotiation"] == "on":
                value = "AUTONEGMODE"
            elif field == "Link detected":
                value = "LINK_UP" if self.ethCache[field] == "yes" else "LINK_DOWN"

        if value:
            self.addResp(response, True, key, value)
        else:
            self.log.error("Unable to obtain value from ethtool cache.")
            self.addResp(response, key=key, errCode=1005)

    ## Handles external flow_control
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def runEthtoola(self, response, key, port, field):
        try:
            out = check_output(["ethtool", "-a", port])
            self.addResp(response, True, key, out.split('\n')[field])
        except CalledProcessError as err:
            self.log.error("Problem running command: %s" % err.cmd)
            self.addResp(response, key=key, errCode=1005)

    ## Handles external vlan key requests
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def getVlan(self, response, key, port, field):
        try:
            # Response from the switch
            jsonResp = self.vtss.callMethod(['vlan.config.interface.get',port])
            if jsonResp["error"] == None:
                for vlan_id in jsonResp['result'][field]:
                    self.addResp(response, True, key, str(vlan_id))
            else:
                self.log.error("Unable to get the VLanId from the switch")
                self.addResp(response, key=key, errCode=1005)
        except Exception:
            self.log.error("Unable to connect to the switch")
            self.addResp(response, key=key, errCode=1005)

    ## Handles external port key requests
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def getPortConfigInfo(self, response, key, port, field):
        # first check if we have the requested value in cache
        if field in self.configCache.keys():
            # we have it!!!
            # Add the response
            self.addResp(response, True, key, self.configCache[field])
            return

        try:
            # Remote Procedure Call
            call = 'port.config.get'
            # Response from the switch
            jsonResp = self.vtss.callMethod([call, port])
            if jsonResp["error"] == None:
                # fill the cache with the received values from the switch
                self.configCache['Shutdown'] = 'True' if jsonResp['result']['Shutdown'] else 'False'
                self.configCache['Speed'] = jsonResp['result']['Speed'].upper()
                self.configCache['FC'] = 'True' if jsonResp['result']['FC'] == "on" else 'False'
                self.configCache['MTU'] = str(jsonResp['result']['MTU'])

                # Add the response
                self.addResp(response, True, key, self.configCache[field])
            else:
                self.log.error('Unable to get "%s" port information from the switch.' % (field))
                self.addResp(response, key=key, errCode=1005)
                self.configCache = {}
        except Exception:
            self.log.error("Unable to connect to the switch")
            self.addResp(response, key=key, errCode=1005)
            self.configCache = {}

    ## Handles external port key requests
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def getPortStatusInfo(self, response, key, port, field):
        # first check if we have the requested value in cache
        if field in self.statusCache.keys():
            # we have it!!!
            # Add the response
            self.addResp(response, True, key, self.statusCache[field])
            return

        try:
            # Remote Procedure Call
            call = 'port.status.get'
            # Response from the switch
            jsonResp = self.vtss.callMethod([call, port])
            if jsonResp["error"] == None:
                # fill the cache with the received values from the switch
                self.statusCache['Speed'] = jsonResp['result']['Speed'].upper()
                self.statusCache['Link'] = 'LINK_UP' if jsonResp['result']['Link'] else 'LINK_DOWN'

                # Add the response
                self.addResp(response, True, key, self.statusCache[field])
            else:
                self.log.error('Unable to get "%s" port information from the switch.' % (field))
                self.addResp(response, key=key, errCode=1005)
                self.statusCache = {}
        except Exception:
            self.log.error("Unable to connect to the switch")
            self.addResp(response, key=key, errCode=1005)
            self.statusCache = {}

    ## Handles unsupported key requests
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def unsupported(self, response, key, port, field):
        self.log.warning("Unsupported key: %s" % key)
        self.addResp(response, key=key, errCode=1001)