from subprocess import call
from datetime import datetime
from common.pb2.rtc_driver_pb2 import *
from tklabs_utils.logger import logger
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.tzmq.ThalesZMQServer import ThalesZMQServer


## RTC DRIVER Simulator class
#  Implements 2 functions according to document MPS RTC Driver ICD:
#    - GetTime: returns the current system time
#    - SetTime: Set the specified system time
class RTCDriverSimulator(ThalesZMQServer):
    ## Constructor
    def __init__(self):
        # Accoding to "MPS Network Configuration" document.
        # TODO: On target system this needs to be 'ipc:///tmp/rtc-drv.sock'. Uncomment next line and comment/remove the other below
        # super(RTCDriverSimulator, self).__init__('ipc:///tmp/rtc-drv.sock')
        super(RTCDriverSimulator, self).__init__('tcp://*:40001')
        # Date-Time pattern.
        self.dateTimePattern = '%Y-%m-%d %H:%M:%SZ'

    ## Called by base class when a request is received from a client.
    #
    #  @param request ThalesZMQMessage object containing received request
    def handleRequest(self, request):
        # Create the empty response
        response = TimeResponse()
        # Route messages based on type
        if request.name == "GetTime":
            response = self.handleGetTimeReq()
        elif request.name == "SetTime":
            response = self.handleSetTimeReq(request)
        else:
            print "Error! Unsupported request type"
            response.error = INVALID_OPERATION

        # Send response back to client
        return ThalesZMQMessage(response)

    ## Handle "GetTime" request
    #
    def handleGetTimeReq(self):
        print "Message Received: GetTime"
        # Create the response
        response = TimeResponse()
        # Error code 0: Success
        response.error = SUCCESS
        response.datetime = datetime.utcnow().strftime(self.dateTimePattern)
        print "Response:\n\tSuccess: %d\n\tDatetime: %s" % (response.error, response.datetime)

        # Send response back to client
        return response

    ## Handle "SetTime" request
    #
    # @param: request
    # @type:  ThalesZMQMessage
    def handleSetTimeReq(self, request):
        print "Message Received: SetTime"
        # Create the response
        response = TimeResponse()

        # Parse request
        set_req = SetTime()
        set_req.ParseFromString(request.serializedBody)
        response.error = SUCCESS

        print "Response:\n\tSuccess: %d" % (response.error)

        # Send response back to client
        return response

if __name__ == "__main__":
    simulator = RTCDriverSimulator()
    simulator.run()
    print "Exit RTC Driver simulator"