
from common.tzmq.ThalesZMQServer import ThalesZMQServer
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.HDDS_pb2 import GetReq, GetResp, SetReq, HDDSSetResp


class HDDSSimulator(ThalesZMQServer):
    def __init__(self):
        super(HDDSSimulator, self).__init__("tcp://*:40001")

        # List of properties that can be get/set
        self.properties = {"carrier_card.switch.temperature": "50.4",
                           "external_pins.input.pin_e7"     : "LOW",
                           "external_pins.input.pin_d7"     : "LOW",
                           "external_pins.input.pin_c7"     : "LOW",
                           "external_pins.input.pin_b7"     : "LOW",
                           "external_pins.input.pin_a7"     : "LOW",
                           "external_pins.input.pin_c8"     : "LOW",
                           "external_pins.output.pin_e8"    : "LOW",
                           "external_pins.output.pin_e6"    : "LOW",
                           "external_pins.output.pin_d6"    : "LOW",
                           "external_pins.output.pin_c6"    : "LOW",
                           "external_pins.output.pin_b6"    : "LOW",
                           "external_pins.output.pin_a6"    : "LOW" }

        # Simulate GPIO loopback by linking outputs to inputs
        self.gpioMap = {"external_pins.output.pin_e8": "external_pins.input.pin_c8",
                        "external_pins.output.pin_e6": "external_pins.input.pin_e7",
                        "external_pins.output.pin_d6": "external_pins.input.pin_d7",
                        "external_pins.output.pin_c6": "external_pins.input.pin_c7",
                        "external_pins.output.pin_b6": "external_pins.input.pin_b7",
                        "external_pins.output.pin_a6": "external_pins.input.pin_a7"}

    def HandleRequest(self, request):
        if request.name == "GetReq":
            # Parse Get request
            getReq = GetReq()
            getReq.ParseFromString(request.serializedBody)

            # Create a GetResp message for the results
            getResp = GetResp()

            # Loop through the key requests
            for key in getReq.key:
                # TODO: support wildcards?
                valueResp = getResp.values.add()
                valueResp.keyValue.key = key
                if key in self.properties:
                    print "Get request:", key
                    valueResp.success = True
                    valueResp.keyValue.value = self.properties[key]
                else:
                    print "Get request for unknown key", key
                    valueResp.success = False
                    valueResp.keyValue.value = ""

            # Send response back to client
            self.SendResponse(ThalesZMQMessage("GetResp", getResp))

        elif request.name == "SetReq":
            # Parse Set request
            setReq = SetReq()
            setReq.ParseFromString(request.serializedBody)

            # Create a HDDSSetResp message for the results
            setResp = HDDSSetResp()

            # Loop through value requests
            for prop in setReq.values:
                valueResp = setResp.values.add()
                valueResp.keyValue.key = prop.key
                if prop.key in self.properties:
                    print "Set request:", prop.key, ":", prop.value
                    self.properties[prop.key] = prop.value
                    valueResp.success = True
                    valueResp.keyValue.value = prop.value
                    # If this is a GPIO output, simulate loopback by setting linked input value
                    if prop.key in self.gpioMap:
                        print "Setting linked GPIO", self.gpioMap[prop.key], ":", prop.value
                        self.properties[self.gpioMap[prop.key]] = prop.value
                else:
                    print "Set request for unknown key", prop.key
                    valueResp.success = False
                    valueResp.keyValue.value = prop.value

            # Send response back to client
            self.SendResponse(ThalesZMQMessage("HDDSSetResp", setResp))

        else:
            print "Error! Unknown request type"
            # Send "Unexpected Message" error back to client
            self.SendUnexpectedMessageErrorResponse()


if __name__ == "__main__":
    simulator = HDDSSimulator()
    simulator.Run()
