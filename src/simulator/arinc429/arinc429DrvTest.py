
import time
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.ARINC429Driver_pb2 import Request, Response

# @cond doxygen_unittest

## ARINC429 Driver Simulator Tester class
#
class ARINC429DriverClient(ThalesZMQClient):
    ## Constructor
    def __init__(self):
        super(ARINC429DriverClient, self).__init__("ipc:///tmp/arinc/driver/429/device")

    ## Sends a RECEIVE_DATA Request message to the simulator and prints the response
    def sendRxRequest(self, channel):
        # Create a request of type RECEIVE_DATA
        rxReq = Request()
        rxReq.channelName = channel
        rxReq.type = Request.RECEIVE_DATA
        print "Request:  Rx", channel, ":"

        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(rxReq))

        # Parse the response
        if response.name == "Response":
            rxResp = Response()
            rxResp.ParseFromString(response.serializedBody)
            if rxResp.errorCode == Response.NONE:
                if len(rxResp.inputData.data) == 0:
                    print "Response: Rx %s : No data available" % rxResp.channelName
                elif len(rxResp.inputData.data) == 1:
                    print "Response: Rx %s : data 0x%x  timestamp %d" % \
                          (rxResp.channelName,
                           rxResp.inputData.data[0].data,
                           rxResp.inputData.data[0].timestamp)
                else:
                    print "Response: Rx", rxResp.channelName, ":", rxResp.inputData
            elif rxResp.errorCode == Response.INVALID_CHANNEL:
                print "Response: Invalid receive channel", rxResp.channelName
            else:
                print "Response: Failed to receive data on", rxResp.channelName
        elif response.name == "ErrorMessage":
            print "Got error message from server"
        else:
            print "Error! Unknown response type"

    ## Sends a Tx Request message to the simulator and prints the response
    def sendTxRequest(self, channel, data):
        # Create a request of type TRANSMIT_DATA
        txReq = Request()
        txReq.channelName = channel
        txReq.type = Request.TRANSMIT_DATA
        word = txReq.outputData.data.add()
        word.data = data
        word.timestamp = int(time.time() * 1000)
        print "Request:  Tx %s : data 0x%x  timestamp %d" % (channel, word.data, word.timestamp)

        # Send a request and get the response
        response = self.sendRequest(ThalesZMQMessage(txReq))

        # Parse the response
        if response.name == "Response":
            txResp = Response()
            txResp.ParseFromString(response.serializedBody)
            if txResp.errorCode == Response.NONE:
                print "Response: Tx", txResp.channelName, ": OK"
            elif txResp.errorCode == Response.INVALID_CHANNEL:
                print "Response: Invalid transmit channel", txResp.channelName
            else:
                print "Response: Failed to transmit data on", txResp.channelName
        elif response.name == "ErrorMessage":
            print "Got error message from server"
        else:
            print "Error! Unknown response type"


if __name__ == "__main__":
    # Create a ARINC429DriverClient instance; this will open a connection to the simulator
    client = ARINC429DriverClient()

    # Send some Tx/Rx requests.
    print "\nTx request with invalid name:"
    client.sendTxRequest("ARINC_429_BOGUS", 0)

    print "\nRx request with invalid name:"
    client.sendRxRequest("ARINC_429_BOGUS")

    print "\nInitial read to get stale data on the channel, if any:"
    client.sendRxRequest("ARINC_429_RX1")

    print "\nSend some valid Tx/Rx requests:"
    for i in range(11):
        print
        time.sleep(0.1)
        client.sendTxRequest("ARINC_429_TX1", (i + 1) << 10)
        client.sendRxRequest("ARINC_429_RX1")

    print "\nRx without a Tx - should get no data:"
    client.sendRxRequest("ARINC_429_RX1")

## @endcond
