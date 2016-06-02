import os
from common.gpb.python import ARINC717Frame_pb2
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.ARINC717Driver_pb2 import Request, Response
from common.module import module

## ARINC717 Module
#
class ARINC717(module.Module):
    ## Constructor
    #  @param   self
    #  @param   config
    def __init__(self, config = {}):
        ## initializes parent class
        super(ARINC717, self).__init__({})
        ## adds handler to available message handlers
        self.addMsgHandler(ARINC717Frame_pb2.ARINC717FrameRequest, self.handler)

        ipcdir = "/tmp/arinc/driver/717"
        if not os.path.exists(ipcdir):
            os.makedirs(ipcdir)

    ## Sends tzmq request message to ARINC717 pripheral
    #
    #  @param     self
    #  @return    client.sendRequest(ThalesZMQMessage(request)) a ThalesZMQMessage object returned from sendRequest()
    def makeRequest(self):
        client = ThalesZMQClient("ipc:///tmp/arinc/driver/717/device")
        request = Request()
        request.type = Request.RECEIVE_FRAME

        return client.sendRequest(ThalesZMQMessage(request))

    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param     self
    #  @param     msg       tzmq format message
    #  @return    reply     a ThalesZMQMessage object
    def handler(self, msg):
        reply = ARINC717Frame_pb2.ARINC717FrameResponse()

        if msg.body.requestType == ARINC717Frame_pb2.ARINC717FrameRequest.RUN:
            reply = self.start()
        elif msg.body.requestType == ARINC717Frame_pb2.ARINC717FrameRequest.STOP:
            reply = self.stop()
        elif msg.body.requestType == ARINC717Frame_pb2.ARINC717FrameRequest.REPORT:
            reply = self.report()
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        return ThalesZMQMessage(reply)

    ## Starts ???
    #
    #  @param     self
    #  @return    self.report() an EthernetResponse object generated by report() function
    def start(self):
        return self.report()

    ## Stops ???
    #
    #  @param     self
    #  @return    self.report() an EthernetResponse object generated by report() function
    def stop(self):
        return self.report()

    ## Reports current ARINC717 Frame status and data
    #
    #  @param     self
    #  @return    reply  an ARINC717FrameResponse object
    def report(self):
        reply = ARINC717Frame_pb2.ARINC717FrameResponse()
        info = Response()
        info.ParseFromString(self.makeRequest().serializedBody)

        reply.state = ARINC717Frame_pb2.ARINC717FrameResponse.RUNNING
        reply.syncState = info.frame.out_of_sync
        data = info.frame.data

        ## turns every two characters in data into 16-bit data
        for char in range(0, len(data), 2):
            reply.arinc717frame.append((ord(data[char]) << 8) | ord(data[char + 1]))

        return reply