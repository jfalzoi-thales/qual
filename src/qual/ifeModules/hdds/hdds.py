import subprocess

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
        self.volts = {"ife.voltage.U130_3V3":1,
                    "ife.voltage.U14_3V3":2,
                    "ife.voltage.U14_5V":3,
                    "ife.voltage.U14_5VMPS":4,
                    "ife.voltage.U14_1V8":5,
                    "ife.voltage.U14_1V2":6,
                    "ife.voltage.U123_3V3":7,
                    "ife.voltage.U123_EXT_3V3":8,
                    "ife.voltage.U123_3V3_SSD1":9,
                    "ife.voltage.U123_3V3_SSD2":10,
                    "ife.voltage.U123_3V3_SSD3":11}
        ## Dict containing temperature specific keys and their sensor ids
        self.temps = {"ife.temperature.U15_TINT":1,
                   "ife.temperature.U15_TR1":2,
                   "ife.temperature.U15_TR2":3,
                   "ife.temperature.U130_3V3":4,
                   "ife.temperature.U14_3V3":5,
                   "ife.temperature.U123_3V3":6}
        #  Add handler to available message handlers
        self.addMsgHandler(HostDomainDeviceServiceRequest, self.handler)

    ## Handles incoming messages
    #  Receives tzmq request and runs requested process
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  ThalesZMQMessage object
    def handler(self, msg):
        response = HostDomainDeviceServiceResponse()

        #  Handle GET requests that start with ife.voltage or ife.temperature
        if msg.body.requestType == HostDomainDeviceServiceRequest.GET:
            keys = []

            for value in msg.body.values:
                if value.key.endswith("*"):
                    if len(value.key.split('.')) == 2:
                        keys += self.volts.keys() + self.temps.keys()
                    elif len(value.key.split('.')) == 3:
                        if value.key.startswith("ife.voltage"):
                            keys += self.volts.keys()
                        elif value.key.startswith("ife.temperature"):
                            keys += self.temps.keys()
                        else:
                            self.log.warning("Unknown key: %s" % value.key)
                    else:
                        self.log.warning("Unknown key: %s" % value.key)
                else:
                    keys.append(value.key)

            for key in keys:
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