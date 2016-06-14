
from common.logger import logger
from common.tzmq.ThalesZMQServer import ThalesZMQServer
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.PowerInfo_pb2 import GetPowerInfo, PowerInfo


## Power Supply Monitor Simulator class
#
# Implements a subset of the Power Supply Monitor Service, as specified
# in the "MPS Power Supply Monitor ICD".  Specifically, it implements
#  the GetPowerInfo message, with the following limitations:
#   - Does not support specifying a single information key in the
#     request; always returns all parameters for the specified device
#     (if device is specified) or all devices (if no device specified)
#   - Values read will always be the same
#
# The Power Supply ZMQ service uses IPC at ipc:///tmp/pwr-supp-mon.sock
# per the "MAP Network Configuration" document.
#
class PowerSupplyMonSimulator(ThalesZMQServer):
    def __init__(self):
        super(PowerSupplyMonSimulator, self).__init__("ipc:///tmp/pwr-supp-mon.sock")

        # Turn down ThalesZMQServer debug level
        self.log.setLevel(logger.INFO)

        # List of devices and properties that can be retrieved.
        # Device names were taken from the example power supply configuration
        # file in the "MPS Power Supply Monitor ICD", and the per-device parameter
        # names were taken from "Appendix A Parameter Names" in the document
        # "MPS Power Supply Monitor Plugin ICD".
        self.properties = {"LTC2990-1": {"VOLTAGE":                      "4.1",
                                         "CURRENT":                      "1234.5",
                                         "EXT_TEMP":                     "33.3",
                                         "INT_TEMP":                     "44.4",
                                         "VCC":                          "5.0"},
                           "LTC2990-2": {"VOLTAGE":                      "4.2",
                                         "CURRENT":                      "1234.5",
                                         "EXT_TEMP":                     "33.3",
                                         "INT_TEMP":                     "44.4",
                                         "VCC":                          "5.0"},
                           "LTC2990-3": {"VOLTAGE":                      "4.3",
                                         "CURRENT":                      "1234.5",
                                         "EXT_TEMP":                     "33.3",
                                         "INT_TEMP":                     "44.4",
                                         "VCC":                          "5.0"},
                           "LTC2990-4": {"VOLTAGE1":                     "4.4",
                                         "VOLTAGE2":                     "4.5",
                                         "EXT_TEMP":                     "33.3",
                                         "INT_TEMP":                     "44.4",
                                         "VCC":                          "5.0"},
                           "LTC2990-5": {"EXT_TEMP1":                    "22.2",
                                         "EXT_TEMP2":                    "33.3",
                                         "INT_TEMP":                     "44.4",
                                         "VCC":                          "5.0"},
                           "LTC2937":   {"SEQ_CHAN_FAULT":               "No fault",
                                         "SEQ_STATUS":                   "Sequence-up in progress",
                                         "SV_OVERVOLT_FAULT":            "No fault",
                                         "SV_UNDERVOLT_FAULT":           "No fault",
                                         "SV_FAULT":                     "No fault",
                                         "MON_BACKUP_REG_STAT":          "MONITOR_BACKUP written"},
                           "ZL6105":    {"INPUT_OVERCURRENT_FAULT":      "No fault",
                                         "INPUT_OVERCURRENT_WARNING":    "No warning",
                                         "INPUT_OVERVOLT_FAULT":         "No fault",
                                         "INPUT_UNDERVOLT_FAULT":        "No fault",
                                         "OVERTEMP_FAULT":               "No fault",
                                         "OVERTEMP_WARNING":             "No warning"},
                           "ZL2102-1":  {"OUTPUT_CURRENT_POWER_BAD":     "No fault",
                                         "OUTPUT_OVERCURRENT_FAULT":     "No fault",
                                         "INPUT_VOLT_CURRENT_POWER_BAD": "No fault",
                                         "TEMPERATURE_BAD":              "No fault"},
                           "ZL2102-2":  {"OUTPUT_CURRENT_POWER_BAD":     "No fault",
                                         "OUTPUT_OVERCURRENT_FAULT":     "No fault",
                                         "INPUT_VOLT_CURRENT_POWER_BAD": "No fault",
                                         "TEMPERATURE_BAD":              "No fault"},
                           "GPIO":      {"PS_OverTemp_Secondary":        "LOW",
                                         "PS_OverTemp_Primary":          "LOW",
                                         "PS_12V_5V_PG":                 "LOW",
                                         "PS_28V_PG":                    "LOW",
                                         "PS_BackupAC":                  "LOW"}}

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleRequest(self, request):
        # We currently only implement the GetPowerInfo message.
        # There is also a SetPowerInfo message, but it doesn't appear we will need it.
        if request.name == "GetPowerInfo":
            # Parse Get request
            getPowerInfo = GetPowerInfo()
            getPowerInfo.ParseFromString(request.serializedBody)

            # Create a PowerInfo message for the results
            powerInfo = PowerInfo()

            if getPowerInfo.name == "":
                # Empty device name means return all params for all devices
                powerInfo.errorCode = PowerInfo.SUCCESS
                for name in self.properties.keys():
                    self.AddAllToResponse(name, powerInfo)
            elif getPowerInfo.name in self.properties:
                # For now, don't allow retrieving specific values, only all values for a device
                # since that's how we'll be using it for the System Monitoring module
                powerInfo.errorCode = PowerInfo.SUCCESS
                self.AddAllToResponse(getPowerInfo.name, powerInfo)
            else:
                print "Get request for unknown device:", getPowerInfo.name
                powerInfo.errorCode = PowerInfo.INVALID_DEVICE_NAME

            # Send response back to client
            return ThalesZMQMessage(powerInfo)

        else:
            print "Error! Unknown request type"
            # Send "Unsupported Message" error back to client
            return self.getUnsupportedMessageErrorResponse()

    def AddAllToResponse(self, name, powerInfo):
        for key, value in self.properties[name].items():
            valueResp = powerInfo.values.add()
            valueResp.name = name
            valueResp.key = key
            valueResp.value = value


if __name__ == "__main__":
    simulator = PowerSupplyMonSimulator()
    simulator.run()
    print "Exit Power Supply Monitor simulator"
