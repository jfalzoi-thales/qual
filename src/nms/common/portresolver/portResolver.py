import os
import ConfigParser

# Config file path
conf_path = '/thales/host/config/system/system.conf'

#  Dictionary with the statics port names
portNames = {
    'external.enet_1' :('Gi 1/14',True),
    'external.enet_2' :('Gi 1/9',True),
    'external.enet_3' :('Gi 1/13',True),
    'external.enet_4' :('Gi 1/10',True),
    'external.enet_5' :('Gi 1/12',True),
    'external.enet_6' :('Gi 1/8',True),
    'external.enet_7' :('Gi 1/11',True),
    'external.enet_8' :('eno1',False),
    'external.enet_9' :('Gi 1/7',True),
    'external.enet_10':('Gi 1/6',True),
    'external.enet_11':('Gi 1/5',True),
    'external.enet_12':('Gi 1/4',True),
    'external.enet_13':('Gi 1/3',True),
    'external.enet_14':('Gi 1/2',True),
    'external.enet_15':('Gi 1/1',True),
    'external.front_panel':('unkown', False),
    #  Internal port names
    'internal.switch_1' :('Gi 1/1',True),
    'internal.switch_2' :('Gi 1/2',True),
    'internal.switch_3' :('Gi 1/3',True),
    'internal.switch_4' :('Gi 1/4',True),
    'internal.switch_5' :('Gi 1/5',True),
    'internal.switch_6' :('Gi 1/6',True),
    'internal.switch_7' :('Gi 1/7',True),
    'internal.switch_8' :('Gi 1/8',True),
    'internal.switch_9' :('Gi 1/9',True),
    'internal.switch_10':('Gi 1/10',True),
    'internal.switch_11':('Gi 1/11',True),
    'internal.switch_12':('Gi 1/12',True),
    'internal.switch_13':('Gi 1/13',True),
    'internal.switch_14':('Gi 1/14',True),
    'internal.switch_15':('Gi 1/15',True),
    'internal.switch_16':('Gi 1/16',True),
    'internal.switch_17':('Gi 1/17',True),
    'internal.switch_18':('Gi 1/18',True),
    'internal.switch_19':('Gi 1/19',True),
    'internal.switch_20':('Gi 1/20',True),
    'internal.i350_1'   :('ens1f0',False),
    'internal.i350_2'   :('ens1f1',False),
    'internal.i350_3'   :('ens1f2',False),
    'internal.i350_4'   :('ens1f3',False)
}

# If name is None, we might be able to resolve it with the config file
configurablesPortNames = {}
if os.path.exists(conf_path):
    conf = ConfigParser.SafeConfigParser()
    # Read the file
    conf.read(conf_path)
    # See if file has the network section
    if conf.has_section(section='network'):
        # Get all touples in network section
        configs = conf.items(section='network')
        # Get the port names of the network section.
        # and create the dictionary with the actual port names
        for aux in configs:
            configurablesPortNames[aux[0]]=aux[1]



## Resolves the VTSS switch port number according with the string passed
#
#  @type:   str
#  @param:  port_str
#  @type:   str
#  @return: port name to the switch. Eg: "Gi 1/25" or "Gi 14/25"
#  @notes: If return None, no port name found
def resolvePort(portName):
    portName = portName.lower()
    #  Look for the name into keys
    name = portNames[portName] if portName in portNames.keys() else None
    # if no name was found, try into the conf file
    name = portNames[configurablesPortNames[portName]] if name == None and portName in configurablesPortNames.keys() else None

    return name