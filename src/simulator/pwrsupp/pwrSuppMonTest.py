
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.PowerInfo_pb2 import GetPowerInfo, PowerInfo

# @cond doxygen_unittest

## Power Supply Monitor Simulator Tester class
#
class PwrSuppMonClient(ThalesZMQClient):
    ## Constructor
    #
    def __init__(self):
        super(PwrSuppMonClient, self).__init__(address="ipc:///tmp/pwr-supp-mon.sock",
                                               requestParts=2, responseParts=1, timeout=500)

    ## Sends a "GetPowerInfo" message to the simulator and prints the response
    #
    def sendGetReq(self, name, key=""):
        # Create a simple (one key) GetReq
        getPowerInfo = GetPowerInfo()
        if name != "":
            print "Request info for device:", name
            getPowerInfo.name = name
            getPowerInfo.key = key
        else:
            print "Request info for all devices"

        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(getPowerInfo))

        # Parse the response
        if response.name == self.defaultResponseName:
            powerInfo = PowerInfo()
            powerInfo.ParseFromString(response.serializedBody)
            if powerInfo.errorCode == PowerInfo.SUCCESS:
                for valueResp in powerInfo.values:
                    print valueResp.name, valueResp.key, ":", valueResp.value
                print
            else:
                print "Request failed with error", powerInfo.errorCode
        elif response.name == "ErrorMessage":
            print "Got error message from server"
        else:
            print "Error! Unknown response type"


if __name__ == "__main__":
    # Create a PwrSuppMonClient instance; this will open a connection to the simulator
    client = PwrSuppMonClient()

    # Send some get requests.
    client.sendGetReq("LTC2990-2", key="CURRENT")
    client.sendGetReq("ZL6105")
    client.sendGetReq("")
    client.sendGetReq("bogus_name")
## @endcond

