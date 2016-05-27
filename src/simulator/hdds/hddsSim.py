
from common.tzmq.ThalesZMQServer import ThalesZMQServer
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.HDDS_pb2 import GetReq, GetResp, SetReq, HDDSSetResp


## HDDS Simulator class
#
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
#
class HDDSSimulator(ThalesZMQServer):
    ## Constructor
    #
    def __init__(self):
        # TODO: On target system this needs to be on VLAN 301, IP address 192.168.1.4
        # per the "MAP Network Configuration" document.
        super(HDDSSimulator, self).__init__("tcp://*:40001")
        print "Started HDDS simulator on", self.address

        # List of properties that can be get/set
        self.properties = {"carrier_card.switch.temperature": "50.4",
                           "external_pins.input.pin_e7":      "LOW",
                           "external_pins.input.pin_d7":      "LOW",
                           "external_pins.input.pin_c7":      "LOW",
                           "external_pins.input.pin_b7":      "LOW",
                           "external_pins.input.pin_a7":      "LOW",
                           "external_pins.input.pin_c8":      "LOW",
                           "external_pins.output.pin_e8":     "LOW",
                           "external_pins.output.pin_e6":     "LOW",
                           "external_pins.output.pin_d6":     "LOW",
                           "external_pins.output.pin_c6":     "LOW",
                           "external_pins.output.pin_b6":     "LOW",
                           "external_pins.output.pin_a6":     "LOW"}

        # Simulate GPIO loopback by linking outputs to inputs
        self.gpioMap = {"external_pins.output.pin_e8": "external_pins.input.pin_c8",
                        "external_pins.output.pin_e6": "external_pins.input.pin_e7",
                        "external_pins.output.pin_d6": "external_pins.input.pin_d7",
                        "external_pins.output.pin_c6": "external_pins.input.pin_c7",
                        "external_pins.output.pin_b6": "external_pins.input.pin_b7",
                        "external_pins.output.pin_a6": "external_pins.input.pin_a7"}

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleRequest(self, request):
        # Route messages based on type
        if request.name == "GetReq":
            self.handleGetReq(request)
        elif request.name == "SetReq":
            self.handleSetReq(request)
        else:
            print "Error! Unsupported request type"
            self.sendUnsupportedMessageErrorResponse()

    ## Handle request of type "GetReq"
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleGetReq(self, request):
        # Parse request
        getReq = GetReq()
        getReq.ParseFromString(request.serializedBody)

        # Create a GetResp message for the results
        getResp = GetResp()

        # Loop through the key requests
        for key in getReq.key:
            # Currently we do not support wildcards, only exact matches
            valueResp = getResp.values.add()
            valueResp.keyValue.key = key
            if key in self.properties:
                # print "Get request:", key
                valueResp.success = True
                valueResp.keyValue.value = self.properties[key]
            else:
                print "Get request for unknown key:", key
                valueResp.success = False
                valueResp.keyValue.value = ""
                valueResp.error.error_code = 1001
                valueResp.error.error_description = "Invalid/unsupported key in HDDS_GET message"

        # Send response back to client
        self.sendResponse(ThalesZMQMessage(getResp))

    ## Handle request of type "SetReq"
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleSetReq(self, request):
        # Parse request
        setReq = SetReq()
        setReq.ParseFromString(request.serializedBody)

        # Create a HDDSSetResp message for the results
        setResp = HDDSSetResp()

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
                valueResp.error.error_code = 1001
                valueResp.error.error_description = "Invalid/unsupported key in HDDS_SET message"

        # Send response back to client
        self.sendResponse(ThalesZMQMessage(setResp))


if __name__ == "__main__":
    simulator = HDDSSimulator()
    simulator.run()
    print "Exit HDDS simulator"
