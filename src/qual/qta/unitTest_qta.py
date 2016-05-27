
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.CPULoading_pb2 import CPULoadingRequest, CPULoadingResponse


## QTA Tester class
#
class QTAClient(ThalesZMQClient):
    ## Constructor
    #
    def __init__(self):
        super(QTAClient, self).__init__("tcp://localhost:50001")

    @staticmethod
    def printResponse(response):
        if response.name == "CPULoadingResponse":
            cpuResponse = CPULoadingResponse()
            cpuResponse.ParseFromString(response.serializedBody)
            print cpuResponse
        elif response.name == "ErrorMessage":
            print "Got error message from server"
        else:
            print "Error! Unknown response type"

    def test_CPULoading(self):
        message = CPULoadingRequest()

        ## test REPORT before CPU load
        message.requestType = CPULoadingRequest.REPORT
        response = self.sendRequest(ThalesZMQMessage(message))
        self.printResponse(response)


if __name__ == "__main__":
    # Create a QTAClient instance; this will open a connection to the QTA
    client = QTAClient()

    # Run some tests
    client.test_CPULoading()
