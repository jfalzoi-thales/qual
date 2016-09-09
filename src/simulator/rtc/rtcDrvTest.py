from common.pb2.rtc_driver_pb2 import *
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


# @cond doxygen_unittest

## RTC Driver Simulator Tester class
class RtcDiverClient(ThalesZMQClient):
    ## Constructor
    def __init__(self):
        super(RtcDiverClient, self).__init__("ipc:///tmp/rtc-drv.sock", msgParts=2)

    ## Sends a "GetTime" message to the simulator and prints the response
    def sendGetTime(self):
        # Create a GetTime
        request = GetTime()
        print "Request sent:  GetTime"
        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(request))
        # Parse the response
        if response.name == "TimeResponse":
            respGet = TimeResponse()
            respGet.ParseFromString(response.serializedBody)
            # Check if succeed
            if respGet.error == SUCCESS:
                print "DateTime received: %s" % (respGet.datetime)
            elif response.name == "ErrorMessage":
                print "Got error message from server, error code %d" % (respGet.error)
        else:
            print "Error! Unknown response type"


    ## Sends a "SetTime" message to the simulator and prints the response
    def sendSetTime(self, time):
        # Create a GetTime
        request = SetTime()
        request.datetime = time
        print "Request sent:  SetTime"
        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(request))
        # Parse the response
        if response.name == "TimeResponse":
            respGet = TimeResponse()
            respGet.ParseFromString(response.serializedBody)
            # Check if succeed
            if respGet.error == SUCCESS:
                print "DateTime set: %s" % (request.datetime)
            elif response.name == "ErrorMessage":
                print "Got error message from server, error code %d" % (respGet.error)
        else:
            print "Error! Unknown response type"


if __name__ == "__main__":
    # times
    time_1 = '2016-09-07 1:54:00Z'
    # Create a RtcDiverClient instance; this will open a connection to the simulator
    client = RtcDiverClient()

    # Send some messages
    client.sendSetTime(time_1)
    client.sendGetTime()

## @endcond