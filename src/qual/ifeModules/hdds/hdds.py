import subprocess

from ifeInventory import IFEInventory
from qual.pb2.HDDS_pb2 import HostDomainDeviceServiceRequest, HostDomainDeviceServiceResponse
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


## HDDS Module for IFE sensors
class IFEHDDS(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        #  Initialize parent class
        super(IFEHDDS, self).__init__(config)
        ## Dict containing voltage specific keys and their sensor ids
        self.volts = {"ife.voltage.U130_3V3": 1,
                      "ife.voltage.U14_3V3": 2,
                      "ife.voltage.U14_5V": 3,
                      "ife.voltage.U14_5VMPS": 4,
                      "ife.voltage.U14_1V8": 5,
                      "ife.voltage.U14_1V2": 6,
                      "ife.voltage.U123_3V3": 7,
                      "ife.voltage.U123_EXT_3V3": 8,
                      "ife.voltage.U123_3V3_SSD1": 9,
                      "ife.voltage.U123_3V3_SSD2": 10,
                      "ife.voltage.U123_3V3_SSD3": 11}
        ## Dict containing temperature specific keys and their sensor ids
        self.temps = {"ife.temperature.U15_TINT": 1,
                      "ife.temperature.U15_TR1": 2,
                      "ife.temperature.U15_TR2": 3,
                      "ife.temperature.U130_3V3": 4,
                      "ife.temperature.U14_3V3": 5,
                      "ife.temperature.U123_3V3": 6}
        ## List of valid ife inventory keys
        self.ifeInventoryKeys = ["inventory.ife.part_number",
                                 "inventory.ife.serial_number",
                                 "inventory.ife.revision",
                                 "inventory.ife.manufacturer_pn",
                                 "inventory.ife.manufacturing_date",
                                 "inventory.ife.manufacturer_name",
                                 "inventory.ife.manufacturer_cage"]
        ## List of valid ife mac_address keys
        self.ifeMacKeys = ["mac_address.ife_video_encoder", "mac_address.ife_microcontroller"]
        ## IFEInventory handler
        self.ifeInventory = IFEInventory(self.log)
        #  Add handler to available message handlers
        self.addMsgHandler(HostDomainDeviceServiceRequest, self.handler)

    ## Handles incoming messages
    #  Receives tzmq request and runs requested process
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  ThalesZMQMessage object
    def handler(self, msg):
        response = HostDomainDeviceServiceResponse()

        if msg.body.requestType == HostDomainDeviceServiceRequest.GET:
            inventoryGetKeys = []
            macGetKeys = []
            sensorGetKeys = []

            for value in msg.body.values:
                if value.key.startswith("inventory.ife"):
                    if value.key in self.ifeInventoryKeys:
                        inventoryGetKeys.append(value.key)
                    else:
                        self.log.error("Attempted to get unrecognized IFE inventory key: %s" % value.key)
                        self.addResp(response, value.key)
                elif value.key.startswith("mac_address.ife"):
                    if value.key in self.ifeMacKeys:
                        macGetKeys.append(value.key)
                    else:
                        self.log.error("Attempted to get unrecognized IFE MAC key: %s" % value.key)
                        self.addResp(response, value.key)
                else:
                    if value.key.endswith("*"):
                        if len(value.key.split('.')) == 2:
                            sensorGetKeys += self.volts.keys() + self.temps.keys()
                        elif len(value.key.split('.')) == 3:
                            if value.key.startswith("ife.voltage"):
                                sensorGetKeys += self.volts.keys()
                            elif value.key.startswith("ife.temperature"):
                                sensorGetKeys += self.temps.keys()
                            else:
                                self.log.warning("Unknown sensor key: %s" % value.key)
                        else:
                            self.log.warning("Unknown sensor key: %s" % value.key)
                    else:
                        if value.key in self.temps or value.key in self.volts:
                            sensorGetKeys.append(value.key)
                        else:
                            self.log.warning("Unknown sensor key: %s" % value.key)

            if inventoryGetKeys: self.inventoryGet(response, inventoryGetKeys)
            if macGetKeys: self.macGet(response, macGetKeys)
            if sensorGetKeys: self.sensorGet(response, sensorGetKeys)
        elif msg.body.requestType == HostDomainDeviceServiceRequest.SET:
            inventorySetPairs = {}

            for value in msg.body.values:
                if value.key in self.ifeInventoryKeys:
                    inventorySetPairs[value.key] = value.value
                else:
                    self.log.warning("Attempted to set unrecognized IFE inventory key: %s" % value.key)
                    self.addResp(response, value.key)

            if inventorySetPairs: self.inventorySet(response, inventorySetPairs)
        else:
            self.log.error("Unexpected Request Type %d" % msg.body.requestType)
            self.addResp(response)

        return ThalesZMQMessage(response)

    ## Adds another set of values to the repeated property response field
    #  @param   self
    #  @param   response    A HostDomainDeviceServiceResponse object
    #  @param   key         Key to be added to response, default empty
    #  @param   value       Value of key to be added to response, default empty
    #  @param   success     Success flag to be added to response, default False
    def addResp(self, response, key="", value="", success=False):
        respVal = response.values.add()
        respVal.key = key
        respVal.value = value
        respVal.success = success

    ## Handles GET requests for IFE inventory keys
    #  @param   self
    #  @param   response        A HostDomainDeviceServiceResponse object
    #  @param   inventoryKeys   A list of keys to return
    def inventoryGet(self, response, inventoryKeys):
        inventoryValues = {}
        self.ifeInventory.read(inventoryValues)

        for key in inventoryKeys:
            if key in inventoryValues:
                self.addResp(response, key, inventoryValues[key], True)
            elif key in self.ifeInventoryKeys:
                self.addResp(response, key, "", True)

    ## Handles GET requests for IFE MAC keys
    #  @param   self
    #  @param   response    A HostDomainDeviceServiceResponse object
    #  @param   macKeys     A list of keys to return
    def macGet(self, response, macKeys):
        for key in macKeys:
            mac = None

            if key == "mac_address.ife_video_encoder":
                if subprocess.call(["videoEncoder.sh", "status"]) == 0:
                    try:
                        out = subprocess.check_output(["arp", "-an"])
                    except subprocess.CalledProcessError as err:
                        self.log.error("Error running command: %s" % err.cmd)
                    else:
                        for line in out.split('\n'):
                            if "192.168.0.65" in line:
                                mac = line.split()[3]
                else:
                    self.log.error("Error running videoEncoder.sh status")
            elif key == "mac_address.ife_microcontroller":
                if subprocess.call(["demo_binaryio", "getDiscreteInput", "LLS_IN_GP_KL_01"]) == 0:
                    try:
                        out = subprocess.check_output(["arp", "-an"])
                    except subprocess.CalledProcessError as err:
                        self.log.error("Error running command: %s" % err.cmd)
                    else:
                        for line in out.split('\n'):
                            if "10.2.69.69" in line:
                                mac = line.split()[3]
                else:
                    self.log.error("Error running demo_binaryio getDiscreteInput LLS_IN_GP_KL_01")

            if mac:
                self.addResp(response, key, mac, True)
            else:
                self.addResp(response, key)

    ## Handles GET requests for IFE sensor keys
    #  @param   self
    #  @param   response    A HostDomainDeviceServiceResponse object
    #  @param   sensorKeys  A list of keys to return
    def sensorGet(self, response, sensorKeys):
        for key in sensorKeys:
            if key.startswith("ife.voltage"):
                try:
                    #  Output Example: LLS_VOLTAGE_SENSOR_ID_1 Chip=0x4d VCC[3P3VDC]=3.26
                    output = subprocess.check_output(["voltsensor", str(self.volts[key])]).rstrip()

                    if output.startswith("LLS_"):
                        elements = output.split("=")
                        self.addResp(response, key, elements[len(elements) - 1], True)
                    else:
                        self.log.warning("Unexpected output: %s" % output)
                        self.addResp(response, key)
                except:
                    self.log.warning("Voltsensor command failed to complete.")
                    self.addResp(response, key)
            elif key.startswith("ife.temperature"):
                try:
                    #  Output Example: LLS_TEMPERATURE_SENSOR_ID_4 Chip=0x4d Internal Temp = 36.50 Celcius
                    output = subprocess.check_output(["tempsensor", str(self.temps[key])]).rstrip()

                    if output.startswith("LLS_"):
                        elements = output.split()
                        self.addResp(response, key, elements[len(elements) - 2], True)
                    else:
                        self.log.warning("Unexpected output: %s" % output)
                        self.addResp(response, key)
                except:
                    self.log.warning("Tempsensor command failed to complete.")
                    self.addResp(response, key)
            else:
                self.log.warning("Unknown key %s" % key)
                self.addResp(response, key)

    ## Handles SET requests for IFE inventory keys
    #  @param   self
    #  @param   response        A HostDomainDeviceServiceResponse object
    #  @param   inventoryPairs  A list of key value pairs to return
    def inventorySet(self, response, inventoryPairs):
        success = self.ifeInventory.update(inventoryPairs)

        for key, value in inventoryPairs.items():
            self.addResp(response, key, value, success)
