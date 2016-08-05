import subprocess
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.HDDS_pb2 import HostDomainDeviceServiceRequest, HostDomainDeviceServiceResponse
from common.module.module import Module

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
        response.key = msg.body.key

        #  Handle GET requests that start with ife.voltage or ife.temperature
        if msg.body.requestType == HostDomainDeviceServiceRequest.GET:
            if msg.body.key.startswith("ife.voltage"):
                try:
                    #  Output Example: LLS_TEMPERATURE_SENSOR_ID_4 Chip=0x4d Internal Temp = 36.50 Celcius
                    output = subprocess.check_output(["voltsensor", str(self.volts[msg.body.key])]).rstrip()

                    if output.startswith("LLS_"):
                        elements = output.split()
                        response.value = elements[len(elements) - 2]
                        response.success = True
                    else:
                        response.success = False
                except:
                    self.log.warning("Voltsensor command failed to complete.")
                    response.success = False
            elif msg.body.key.startswith("ife.temperature"):
                try:
                    #  Output Example: LLS_VOLTAGE_SENSOR_ID_1 Chip=0x4d VCC[3P3VDC]=3.26
                    output = subprocess.check_output(["tempsensor", str(self.temps[msg.body.key])]).rstrip()

                    if output.startswith("LLS_"):
                        elements = output.split("=")
                        response.value = elements[len(elements) - 1]
                        response.success = True
                    else:
                        response.success = False
                except:
                    self.log.warning("Tempsensor command failed to complete.")
                    response.success = False
            else:
                self.log.warning("Unknown key %s" % msg.body.key)
                response.success = False
        else:
            self.log.error("Unexpected Request Type %d" % msg.body.requestType)
            response.success = False

        return ThalesZMQMessage(response)
