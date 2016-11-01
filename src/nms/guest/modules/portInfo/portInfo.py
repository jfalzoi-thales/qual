import collections
import os
from subprocess import check_output, CalledProcessError

from nms.common.portresolver.portResolver import resolvePort, portNames, updatePorts,resolveAlias
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
        self.keyInfo = collections.namedtuple("keyInfo", "inFunc inField outFunc outField")
        ## Dict containing possible keys and their functions
        self.portFuncs = {"shutdown":         self.keyInfo(self.getIpLinkData, "state",            self.getPortConfigInfo, "Shutdown"),
                          "speed":            self.keyInfo(self.getEthData,    "Speed",            self.getPortStatusInfo, "Speed"),
                          "configured_speed": self.keyInfo(self.getEthData,    "Auto-negotiation", self.getPortConfigInfo, "Speed"),
                          "flow_control":     self.keyInfo(self.runEthtoola,   0,                  self.getPortConfigInfo, "FC"),
                          "MTU":              self.keyInfo(self.getIpLinkData, "mtu",              self.getPortConfigInfo, "MTU"),
                          "link":             self.keyInfo(self.getEthData,    "Link detected",    self.getPortStatusInfo, "Link"),
                          "vlan_id":          self.keyInfo(self.getInVlans,    0,                  self.getPortVlans     , "TrunkVlans"),
                          "BPDU_state":       self.keyInfo(self.notApplicable, 0,                  self.tempFunc         ,  0)}
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
        ## Device name of the I350
        self.i350EthernetDev="ens1f"
        # Load config file
        self.loadConfig(attributes=('switchAddress','i350EthernetDev'))
        ## Object to call the RPC
        self.vtss = Vtss(switchIP=self.switchAddress)
        #  Adds handler to available message handlers
        self.addMsgHandler(PortInfoReq, self.handler)
        # Update the enet_8 and i350 port names
        updatePorts(self)

    ## Handles incoming messages
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  ThalesZMQMessage object
    def handler(self, msg):
        response = PortInfoResp()

        if msg.body != None:
            for key in msg.body.portInfoKey:
                keyParts = key.split('.')

                if "*" in keyParts:
                    if len(keyParts) == 1:
                        keyParts += ["*", "*"]
                    elif len(keyParts) == 2:
                        # Determine if an alias was passed
                        aliasPassed = resolveAlias(keyParts[0])
                        if aliasPassed[1]:
                            keyParts=aliasPassed[0].split(".")
                        if keyParts[0] == "*":
                            keyParts = ["*"] + keyParts
                        else:
                            keyParts += ["*"]

                    self.wild(response, keyParts, aliasPassed[1], aliasPassed[0])
                elif keyParts[-1] in self.portFuncs:
                    # Try to resolve in case of an alias
                    auxName = ""
                    for name in keyParts[:-1]:
                        auxName += name + "."
                    portName = resolveAlias(auxName[:-1])[0]
                    port = resolvePort(portName)

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
                        self.addResp(response, key=key, errCode=1003, errDesc="Unknown key: %s" % key)
                else:
                    self.addResp(response, key=key, errCode=1004, errDesc="Invalid key: %s" % key)
        else:
            self.wild(response, ["*", "*", "*"])

        return ThalesZMQMessage(response)

    ## Adds another set of values to the repeated values response field
    #  @param   self
    #  @param   response    A PortInfoResp object
    #  @param   success     Success flag to be added to response, default False
    #  @param   key         Key to be added to response, default empty
    #  @param   value       Value of key to be added to response, default empty
    #  @param   errCode     Error code for optional ErrorMessage field
    def addResp(self, response, success=False, key="", value="",  errCode=None, errDesc=""):
        respVal = response.values.add()
        respVal.success = success
        respVal.keyValue.key = key
        respVal.keyValue.value = value

        if errCode:
            self.log.error(errDesc)
            respVal.error.error_code = errCode
            respVal.error.error_description = errDesc

    ## Handles wildcards (*) in requested keys
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   keyParts  Key split on last separator
    def wild(self, response, keyParts, aliasResolved=False, aliasName=""):
        locs = ["internal", "external"] if keyParts[0] == "*" else [keyParts[0]]
        stats = self.portFuncs.keys() if keyParts[2] == "*" else [keyParts[2]]

        if keyParts[1] == "*":
            devs = {name for loc in locs for name in portNames if name.startswith(loc)}
        else:
            devs = {loc + "." + keyParts[1] for loc in locs if loc + "." + keyParts[1] in portNames}

        for dev in devs:
            self.ethCache = {}
            self.ipLinkCache = {}
            self.configCache = {}
            self.statusCache = {}

            for stat in stats:
                port = resolvePort(dev)
                self.callFunc(response, (aliasName if aliasResolved else dev) + "." + stat, stat, port[0], port[1])

    ## Calls appropriate function with specified parameters
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   stat      Requested statistic
    #  @param   port      Port name for function calls
    #  @param   external  True if port is external, False if port is internal
    def callFunc(self, response, key, stat, port, external=True):
        call = self.portFuncs[stat]

        if external:
            call.outFunc(response, key, port, call.outField)
        else:
            call.inFunc(response, key, port, call.inField)

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

    ## Handles inside key requests with data stored in ipLinkCache
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def getIpLinkData(self, response, key, port, field):
        value = None

        if not self.ipLinkCache: self.runIpLinkShow(port)

        if field in self.ipLinkCache:
            if field == "state":
                value = "POWERED" if self.ipLinkCache[field] == "UP" else "SHUTDOWN"
            elif field == "mtu":
                value = bytes(self.ipLinkCache[field])

        if value:
            self.addResp(response, True, key, value)
        else:
            self.addResp(response, key=key, errCode=1005, errDesc="Unable to obtain value from ip link show")

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

    ## Handles inside key requests with data stored in ethCache
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
        errCode = 1005
        errDesc = "Unable to obtain value from ethtool"

        if not self.ethCache: self.runEthtool(port)

        if field in self.ethCache:
            if field == "Speed" or [field == "Auto-negotiation" and self.ethCache[field] != "on"]:
                if self.ethCache["Link detected"] == "yes":
                    speed = self.ethCache["Speed"].rstrip('Mb/s')
                    force = portSpeed[speed] if speed in portSpeed else ""
                    duplex = "FDX" if self.ethCache["Duplex"] == "Full" else "HDX"
                    value = force + duplex
                else:
                    errCode = 1002
                    errDesc = "Link is down, unable to return speed"
            elif field == "Auto-negotiation" and self.ethCache["Auto-negotiation"] == "on":
                value = "AUTONEGMODE"
            elif field == "Link detected":
                value = "LINK_UP" if self.ethCache[field] == "yes" else "LINK_DOWN"

        if value:
            self.addResp(response, True, key, value)
        else:
            self.addResp(response, key=key, errCode=errCode, errDesc=errDesc)

    ## Handles inside flow_control key requests
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
            self.addResp(response, key=key, errCode=1005, errDesc="Problem running command: %s" % err.cmd)

    ## Handles inside VLAN key requests
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def getInVlans(self, response, key, port, field):
        # Only applicable to I350 ports
        if not port.startswith(self.i350EthernetDev):
            self.notApplicable(response, key, port, field)
            return

        # VLAN info comes from /proc entries managed by igb (I350) driver
        pf = int(port[-1]) + 1
        procPath = "/proc/driver/igb/vlans/pf_%d" % pf
        if not os.path.exists(procPath):
            self.addResp(response, key=key, errCode=1005, errDesc="Cannot get VLAN info for I350 PF%d" % pf)
        else:
            with open(procPath, 'r') as procFile:
                contents = procFile.read(256)
            for line in contents.splitlines():
                fields = line.split()
                if len(fields) > 1:
                    self.addResp(response, True, key, fields[1])

    ## Handles switch port VLAN key requests
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def getPortVlans(self, response, key, port, field):
        try:
            # Response from the switch
            jsonResp = self.vtss.callMethod(['vlan.config.interface.get',port])
            if jsonResp["error"] == None:
                # We'll set the vlan_id according to the current port mode
                # Access mode
                if jsonResp['result']['Mode'] == 'access':
                    self.addResp(response, True, key, str(jsonResp['result']['AccessVlan']))
                # Trunk mode
                elif jsonResp['result']['Mode'] == 'trunk':
                    for vlan_id in jsonResp['result']['TrunkVlans']:
                        self.addResp(response, True, key, str(vlan_id))
                # Hybrid mode
                elif jsonResp['result']['Mode'] == 'hybrid':
                    for vlan_id in jsonResp['result']['HybridVlans']:
                        self.addResp(response, True, key, str(vlan_id))
            else:
                self.addResp(response, key=key, errCode=1005, errDesc="Unable to get the VLanId from the switch")
        except Exception:
            self.addResp(response, key=key, errCode=1005, errDesc="Unable to connect to the switch")

    ## Retrieves vtss switch port info
    #  @param   self
    #  @param   port    Port name for function calls
    #  @param   type    Info type to retrieve (config or status)
    def getVtssInfo(self, port, type):
        callType = 'port.' + type + '.get'

        try:
            # Response from the switch
            jsonResp = self.vtss.callMethod([callType, port])
        except Exception:
            self.log.error("Unable to connect to the switch")
        else:
            if jsonResp["error"] == None:
                # fill the cache with the received values from the switch
                if type == 'config':
                    self.configCache['Shutdown'] = 'True' if jsonResp['result']['Shutdown'] else 'False'
                    self.configCache['Speed'] = jsonResp['result']['Speed'].upper()
                    self.configCache['FC'] = 'True' if jsonResp['result']['FC'] == "on" else 'False'
                    self.configCache['MTU'] = str(jsonResp['result']['MTU'])
                elif type == 'status':
                    self.statusCache['Speed'] = jsonResp['result']['Speed'].upper()
                    self.statusCache['Link'] = 'LINK_UP' if jsonResp['result']['Link'] else 'LINK_DOWN'
            else:
                self.log.error("JSON request returned error: %s" % jsonResp["error"])

    ## Handles switch port status key requests
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def getPortConfigInfo(self, response, key, port, field):
        # If cache is empty, populate it
        if not self.configCache: self.getVtssInfo(port, 'config')

        if field in self.configCache:
            self.addResp(response, True, key, self.configCache[field])
        else:
            self.addResp(response, key=key, errCode=1005, errDesc="Unable to retrieve info for port %s from switch" % port)

    ## Handles switch port status key requests
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def getPortStatusInfo(self, response, key, port, field):
        # If cache is empty, populate it
        if not self.statusCache: self.getVtssInfo(port, 'status')

        if field in self.statusCache:
            # If link is down, speed is invalid
            if field != 'Speed' or self.statusCache['Link'] != "LINK_DOWN":
                self.addResp(response, True, key, self.statusCache[field])
            else:
                self.addResp(response, key=key, errCode=1002,errDesc="Link is down, unable to return speed")
        else:
            self.addResp(response, key=key, errCode=1005, errDesc="Unable to retrieve info for port %s from switch" % port)

    ## Handles key requests that are not applicable to this type of port
    #  @param   self
    #  @param   response  PortInfoResp object
    #  @param   key       Requested key
    #  @param   port      Port name for function calls
    #  @param   field     Field to retrieve from cache
    def notApplicable(self, response, key, port, field):
        # Returning an empty string as the value, because it's not really an error
        self.addResp(response, True, key, "")
