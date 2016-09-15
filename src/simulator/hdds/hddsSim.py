from common.pb2.HDDS_API_pb2 import GetReq, GetResp, SetReq, SetResp, FAILURE_INVALID_KEY
from tklabs_utils.logger import logger
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.tzmq.ThalesZMQServer import ThalesZMQServer


## HDDS Simulator class
# Implements a subset of the Host Domain Device Service, as specified
# in the "MPS Host Domain Device Service ICD".  Specifically, it
# implements the GetReq and SetReq messages, with the following limitations:
#   - Wildcards are not supported in GetReq
#   - The list of supported keys is very small (but easily added to)
#   - No error checking for read-only keys
#   - Values read will always be the same, unless changed by SetReq
#
# The HDDS ZMQ service binds to TCP port 40001, per the "MAP Network
# Configuration" document.
#
# In addition, GPIO loopback is simulated by having a static table that
# defines output to input connections, and whenever an output pin in that
# table is changed by SetReq, the linked input pin's value is changed.
class HDDSSimulator(ThalesZMQServer):
    ## Constructor
    def __init__(self):
        # TODO: On target system this needs to be on VLAN 301, IP address 192.168.1.4
        # per the "MAP Network Configuration" document.
        super(HDDSSimulator, self).__init__("tcp://*:40001")

        # Turn down ThalesZMQServer debug level
        self.log.setLevel(logger.INFO)
        # List of properties that can be get/set
        self.properties = {"carrier_card.switch.temperature": "50.4",
                           "external_pins.input.pin_a_d13":   "LOW",
                           "external_pins.input.pin_a_b14":   "LOW",
                           "external_pins.input.pin_a_b13":   "LOW",
                           "external_pins.input.pin_a_c15":   "LOW",
                           "external_pins.input.pin_a_a15":   "LOW",
                           "external_pins.input.pin_b_a8":    "LOW",
                           "external_pins.output.pin_a_e15":  "LOW",
                           "external_pins.output.pin_a_d14":  "LOW",
                           "external_pins.output.pin_a_d15":  "LOW",
                           "external_pins.output.pin_a_c14":  "LOW",
                           "external_pins.output.pin_a_c13":  "LOW",
                           "external_pins.output.pin_a_a13":  "LOW",
                           "power_supply.28V_monitor.voltage":              "28.375256",
                           "power_supply.28V_monitor.current":              "1.845365",
                           "power_supply.28V_monitor.external_temperature": "38.375000",
                           "power_supply.28V_monitor.internal_temperature": "41.000000"}
        # Simulate GPIO loopback by linking outputs to inputs
        self.gpioMap = {"external_pins.output.pin_a_e15": "external_pins.input.pin_a_d13",
                        "external_pins.output.pin_a_d14": "external_pins.input.pin_a_b14",
                        "external_pins.output.pin_a_d15": "external_pins.input.pin_a_b13",
                        "external_pins.output.pin_a_c14": "external_pins.input.pin_a_c15",
                        "external_pins.output.pin_a_c13": "external_pins.input.pin_a_a15",
                        "external_pins.output.pin_a_a13": "external_pins.input.pin_b_a8"}

    ## Called by base class when a request is received from a client.
    # @param request ThalesZMQMessage object containing received request
    def handleRequest(self, request):
        # Route messages based on type
        if request.name == "GetReq":
            return self.handleGetReq(request)
        elif request.name == "SetReq":
            return self.handleSetReq(request)
        else:
            print "Error! Unsupported request type"

            return self.getUnsupportedMessageErrorResponse()

    ## Handle request of type "GetReq"
    # @param request ThalesZMQMessage object containing received request
    def handleGetReq(self, request):
        # Parse request
        getReq = GetReq()
        getReq.ParseFromString(request.serializedBody)
        # Create a GetResp message for the results
        getResp = GetResp()
        getResp.success = False

        # Loop through the key requests
        for key in getReq.key:

            if key.endswith('*'):
                key = key.rstrip('*')
                for k, v in self.properties.items():
                    if k.startswith(key):
                        valueResp = getResp.values.add()
                        valueResp.success = True
                        valueResp.keyValue.key = k
                        valueResp.keyValue.value = v
                # TODO: If wildcard didn't match anything, send failure response
            elif key in self.properties:
                # print "Get request:", key
                valueResp = getResp.values.add()
                valueResp.success = True
                valueResp.keyValue.key = key
                valueResp.keyValue.value = self.properties[key]
            else:
                print "Get request for unknown key:", key
                valueResp = getResp.values.add()
                valueResp.success = False
                valueResp.keyValue.key = key
                valueResp.keyValue.value = ""
                valueResp.error.error_code = FAILURE_INVALID_KEY
                valueResp.error.error_description = "Invalid/unsupported key in HDDS_GET message"

        # If any value in values is successful, consider getResp successful
        for value in getResp.values:
            if value.success == True:
                getResp.success = True

                return ThalesZMQMessage(getResp)

        # Send response back to client
        return ThalesZMQMessage(getResp)

    ## Handle request of type "SetReq"
    # @param request ThalesZMQMessage object containing received request
    def handleSetReq(self, request):
        # Parse request
        setReq = SetReq()
        setReq.ParseFromString(request.serializedBody)
        # Create a HDDSSetResp message for the results
        setResp = SetResp()
        setResp.success = False

        # Loop through value requests
        for prop in setReq.values:
            valueResp = setResp.values.add()
            valueResp.keyValue.key = prop.key

            if prop.key in self.properties:
                # print "Set request:", prop.key, ":", prop.value
                self.properties[prop.key] = prop.value
                valueResp.success = True
                valueResp.keyValue.value = prop.value

                # If this is a GPIO output, simulate loopback by setting linked input value
                if prop.key in self.gpioMap:
                    print "Setting linked GPIO", self.gpioMap[prop.key], ":", prop.value
                    self.properties[self.gpioMap[prop.key]] = prop.value
            else:
                print "Set request for unknown key:", prop.key
                valueResp.success = False
                valueResp.keyValue.value = prop.value
                valueResp.error.error_code = FAILURE_INVALID_KEY
                valueResp.error.error_description = "Invalid/unsupported key in HDDS_SET message"

        # If any value in values is successful, consider setResp successful
        for value in setResp.values:
            if value.success == True:
                setResp.success = True

                return ThalesZMQMessage(setResp)

        # Send response back to client
        return ThalesZMQMessage(setResp)

if __name__ == "__main__":
    simulator = HDDSSimulator()
    simulator.run()
    print "Exit HDDS simulator"