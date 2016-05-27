
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.HDDS_pb2 import GetReq, GetResp, SetReq, HDDSSetResp


## HDDS Simulator Tester class
#
class HDDSClient(ThalesZMQClient):
    ## Constructor
    #
    def __init__(self):
        super(HDDSClient, self).__init__("tcp://localhost:40001")

    ## Sends a "GetReq" message to the simulator and prints the response
    #
    def sendGetReq(self, key):
        # Create a simple (one key) GetReq
        getReq = GetReq()
        getReq.key.append(key)
        print "Request:  Get", key

        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(getReq))

        # Parse the response
        if response.name == "GetResp":
            getResp = GetResp()
            getResp.ParseFromString(response.serializedBody)
            for valueResp in getResp.values:
                if valueResp.success:
                    print "Response: Get", valueResp.keyValue.key, ":", valueResp.keyValue.value
                else:
                    print "Response: Failed to get", valueResp.keyValue.key
        elif response.name == "ErrorMessage":
            print "Got error message from server"
        else:
            print "Error! Unknown response type"

    ## Sends a "SetReq" message to the simulator and prints the response
    #
    def sendSetReq(self, key, value):
        # Create a simple (one property) SetReq
        setReq = SetReq()
        prop = setReq.values.add()
        prop.key = key
        prop.value = value
        print "Request:  Set", key, ":", value

        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(setReq))

        # Parse the response
        if response.name == "HDDSSetResp":
            setResp = HDDSSetResp()
            setResp.ParseFromString(response.serializedBody)
            for valueResp in setResp.values:
                if valueResp.success:
                    print "Response: Set", valueResp.keyValue.key, ":", valueResp.keyValue.value
                else:
                    print "Response: Failed to set", valueResp.keyValue.key
        elif response.name == "ErrorMessage":
            print "Got error message from server"
        else:
            print "Error! Unknown response type"


if __name__ == "__main__":
    # Create a HDDSClient instance; this will open a connection to the simulator
    client = HDDSClient()

    # Send some get/set requests.  Note these only test requests with a single key.
    client.sendGetReq("carrier_card.switch.temperature")
    client.sendGetReq("external_pins.output.pin_e6")
    client.sendGetReq("external_pins.input.pin_e7")
    client.sendSetReq("external_pins.output.pin_e6", "HIGH")
    client.sendGetReq("external_pins.output.pin_e6")
    client.sendGetReq("external_pins.input.pin_e7")
    client.sendSetReq("external_pins.output.pin_e6", "LOW")
    client.sendGetReq("external_pins.output.pin_e6")
    client.sendGetReq("external_pins.input.pin_e7")
    client.sendGetReq("bogus_key")
    client.sendSetReq("bogus_key", "x")

