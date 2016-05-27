
from time import sleep
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.classFinder.classFinder import ClassFinder
from common.logger.logger import Logger
from google.protobuf.message import Message
from common.gpb.python import CPULoading_pb2


## QTA Tester class
#
class QTAClient(ThalesZMQClient):
    ## Constructor
    #
    def __init__(self):
        super(QTAClient, self).__init__("tcp://localhost:50001")

        # Set up a ClassFinder for GPB message classes
        self.gpbClasses = ClassFinder(rootPath='common.gpb.python',
                                      baseClass=Message)
        # Set up a logger
        self.log = Logger(name='Test QTA')

    def sendAndLogResponse(self, request):
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

    def test_CPULoading(self):
        message = CPULoading_pb2.CPULoadingRequest()

        ## test REPORT before CPU load
        self.log.info("REPORT before CPU load:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage(message)
        self.sendAndLogResponse(request)
        sleep(3)

        ## test RUN message with default level input and report
        self.log.info("RUN with default level and report:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.RUN
        request = ThalesZMQMessage(message)
        self.sendAndLogResponse(request)
        sleep(3)

        ## test REPORT message input after CPU load
        self.log.info("REPORT after CPU load:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage(message)
        self.sendAndLogResponse(request)
        sleep(3)

        ## test additional RUN with custom level
        self.log.info("RUN again with custom level while previous load running:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.RUN
        message.level = 50
        request = ThalesZMQMessage(message)
        self.sendAndLogResponse(request)
        sleep(3)

        ## test REPORT message input after additional RUN and custom level
        self.log.info("REPORT after starting additional load with custom level:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage(message)
        self.sendAndLogResponse(request)
        sleep(3)

        ## test STOP message input and report
        self.log.info("STOP and report:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.STOP
        request = ThalesZMQMessage(message)
        self.sendAndLogResponse(request)
        sleep(3)

        ## test REPORT message input after CPU load stop
        self.log.info("REPORT after stopping load:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage(message)
        self.sendAndLogResponse(request)
        sleep(3)

        ## test STOP with no load
        self.log.info("STOP with no load:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.STOP
        request = ThalesZMQMessage(message)
        self.sendAndLogResponse(request)
        sleep(3)

        ## test REPORT message input after stopping with no load
        self.log.info("REPORT after stopping with no load:")
        message.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
        request = ThalesZMQMessage(message)
        self.sendAndLogResponse(request)
        sleep(3)



if __name__ == "__main__":
    # Create a QTAClient instance; this will open a connection to the QTA
    client = QTAClient()

    # Run some tests
    client.test_CPULoading()
