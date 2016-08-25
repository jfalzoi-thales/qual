from time import sleep
from google.protobuf.message import Message

from qual.pb2.CPULoading_pb2 import CPULoadingRequest
from qual.pb2.RS232_pb2 import RS232Request
from tklabs_utils.classFinder.classFinder import ClassFinder
from tklabs_utils.logger.logger import Logger
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


# @cond doxygen_unittest

## QTA Tester class
#
class QTAClient(ThalesZMQClient):
    ## Constructor
    #
    def __init__(self):
        super(QTAClient, self).__init__("tcp://localhost:50001")

        # Set up a ClassFinder for GPB message classes
        self.gpbClasses = ClassFinder(rootPath='qual.pb2',
                                      baseClass=Message)
        # Set up a logger
        self.log = Logger(name='Test QTA')

    ## Send a request to the QTA, wait for the response, and write decoded response to log
    #
    def sendReqAndLogResp(self, request):
        # Send request and get response
        response = self.sendRequest(request)
        self.log.info("Sent %s" % request.name)

        # Look up response type in our ClassFinder
        responseClass = self.gpbClasses.getClassByName(response.name)
        if responseClass is None:
            self.log.warning("Received unknown message class %s" % response.name)
        else:
            # Deserialize the response body and print it
            responseBody = responseClass()
            responseBody.ParseFromString(response.serializedBody)
            self.log.info("Received %s:\n%s" % (response.name, responseBody))

    ## Series of tests for the CPULoading module
    #
    def test_CPULoading(self):
        message = CPULoadingRequest()

        self.log.info("REPORT before CPU load:")
        message.requestType = CPULoadingRequest.REPORT
        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(3)

        self.log.info("RUN with default level and report:")
        message.requestType = CPULoadingRequest.RUN
        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(3)

        self.log.info("REPORT after CPU load:")
        message.requestType = CPULoadingRequest.REPORT
        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(3)

        self.log.info("RUN again with custom level while previous load running:")
        message.requestType = CPULoadingRequest.RUN
        message.level = 50
        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(3)

        self.log.info("REPORT after starting additional load with custom level:")
        message.requestType = CPULoadingRequest.REPORT
        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(3)

        self.log.info("STOP and report:")
        message.requestType = CPULoadingRequest.STOP
        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(3)

        self.log.info("REPORT after stopping load:")
        message.requestType = CPULoadingRequest.REPORT
        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(3)

        self.log.info("STOP with no load:")
        message.requestType = CPULoadingRequest.STOP
        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(3)

        self.log.info("REPORT after stopping with no load:")
        message.requestType = CPULoadingRequest.REPORT
        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(3)

    ## Series of tests for the RS232 module
    #
    def test_RS232(self):
        message = RS232Request()

        self.log.info("Get report before starting:")
        message.requestType = RS232Request.REPORT
        self.sendReqAndLogResp(ThalesZMQMessage(message))

        self.log.info("Start RS232 traffic:")
        message.requestType = RS232Request.RUN
        self.sendReqAndLogResp(ThalesZMQMessage(message))

        self.log.info("Get reports for 10 seconds:")
        message.requestType = RS232Request.REPORT
        for loop in range(10):
            sleep(1)
            self.sendReqAndLogResp(ThalesZMQMessage(message))

        self.log.info("Stop RS232 traffic:")
        message.requestType = RS232Request.STOP
        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(1)

        self.log.info("Get report after stopping:")
        message.requestType = RS232Request.REPORT
        self.sendReqAndLogResp(ThalesZMQMessage(message))


if __name__ == "__main__":
    # Create a QTAClient instance; this will open a connection to the QTA
    client = QTAClient()

    # Run some tests
    client.test_CPULoading()
    client.test_RS232()
## @endcond
