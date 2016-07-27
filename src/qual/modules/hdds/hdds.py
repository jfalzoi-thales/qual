import subprocess
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.HDDS_pb2 import HostDomainDeviceServiceRequest, HostDomainDeviceServiceResponse
from common.gpb.python.HDDS_API_pb2 import GetReq, GetResp, SetReq, SetResp
from common.gpb.python.ErrorMessage_pb2 import ErrorMessage
from common.module.module import Module

## HDDS Module
class HDDS(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        #  Initialize parent class
        super(HDDS, self).__init__(config)
        ## Client connection to the Host Domain Device Service
        self.hddsClient = ThalesZMQClient("tcp://localhost:40001", log=self.log)
        ## Dict containing voltage specific keys and their sensor ids
        self.volts = {"ife.voltage.U130_3V3":1,
                    "ife.voltage.U14_3V3":2,
                    "ife.voltage.U14_5V":3,
                    "ife.voltage.U14_5VMPS":4,
                    "ife.voltage.U14_1V8":5,
                    "ife.voltage.U14_1V2":6,
                    "ife.voltage.U123_3V3":7,
                    "ife.voltage.U123_EXT_3V3":8,
                    "ife.voltage.U123_3V3_SSD1":9,
                    "ife.voltage.U123_3V3_SSD2":10,
                    "ife.voltage.U123_3V3_SSD3":11}
        ## Dict containing temperature specific keys and their sensor ids
        self.temps = {"ife.temperature.U15_TINT":1,
                   "ife.temperature.U15_TR1":2,
                   "ife.temperature.U15_TR2":3,
                   "ife.temperature.U130_3V3":4,
                   "ife.temperature.U14_3V3":5,
                   "ife.temperature.U123_3V3":6}
        #  Add handler to available message handlers
        self.addMsgHandler(HostDomainDeviceServiceRequest, self.handler)

    ## Handles incoming messages
    #  Receives tzmq request and runs requested process
    #  @param   self
    #  @param   msg   tzmq format message
    #  @return  ThalesZMQMessage object
    def handler(self, msg):
        response = HostDomainDeviceServiceResponse()
        response.key = msg.body.key

        #  For get and set messages, check if the key requests is ife.voltage or ife.temperature, if it is, handle it,
        #  otherwise, pass the message through to the HDDS
        if msg.body.requestType == HostDomainDeviceServiceRequest.GET:
            if msg.body.key.startswith("ife.voltage"):
                try:
                    response.value = subprocess.check_output(["voltsensor", self.volts[msg.body.key]])
                    response.success = True
                except:
                    self.log.warning("Voltsensor command failed to complete.")
                    response.success = False
            elif msg.body.key.startswith("ife.temperature"):
                try:
                    response.value = subprocess.check_output(["tempsensor", self.temps[msg.body.key]])
                    response.success = True
                except:
                    self.log.warning("Tempsensor command failed to complete.")
                    response.success = False
            else:
                self.getHandler(response, msg.body)
        elif msg.body.requestType == HostDomainDeviceServiceRequest.SET:
            if msg.body.key.startswith(("ife.voltage", "ife.temperature")):
                response.value = ""
                response.success = False
                self.log.warning("Attempted to set ife voltage or temperature.  Nothing to do.")
            else:
                self.setHandler(response, msg.body)
        else:
            self.log.error("Unexpected Request Type %d" % (msg.body.requestType))

        return ThalesZMQMessage(response)

    ## Handles incoming GET requests
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    def getHandler(self, response, request):
        getReq = GetReq()
        getReq.key.append(request.key)
        # Just pass through to the actual HDDS service
        HDDSResp = self.hddsClient.sendRequest(ThalesZMQMessage(getReq))

        # Check that we got back the expected response and deserialize for debugging purposes
        if HDDSResp.name == "GetResp":
            getResp = GetResp()
            getResp.ParseFromString(HDDSResp.serializedBody)
            response.success = getResp.success
            response.value = getResp.values[0].keyValue.value if getResp.success else ""
        else:
            response.value = ""
            response.success = False

            if HDDSResp.name == "ErrorMessage":
                err = ErrorMessage()
                err.ParseFromString(HDDSResp.serializedBody)
                self.log.warning("Got error message from HDDS: %s" % err.error_description)
            elif HDDSResp.name == "":
                self.log.warning("Get failed: No response from HDDS")
            else:
                self.log.warning("Unexpected response from HDDS: %s" % HDDSResp.name)

    ## Handles incoming SET requests
    #  @param     self
    #  @param     response  HostDomainDeviceServiceResponse object
    #  @param     value     Value to set key to
    def setHandler(self, response, request):
        setReq = SetReq()
        req = setReq.values.add()
        req.key = request.key
        req.value = request.value
        # Just pass through to the actual HDDS service
        HDDSResp = self.hddsClient.sendRequest(ThalesZMQMessage(setReq))

        # Check that we got back the expected response and deserialize for debugging purposes
        if HDDSResp.name == "SetResp":
            setResp = SetResp()
            setResp.ParseFromString(HDDSResp.serializedBody)
            response.success = setResp.success
            response.value = setResp.values[0].keyValue.value if setResp.success else ""
        else:
            response.value = ""
            response.success = False

            if HDDSResp.name == "ErrorMessage":
                err = ErrorMessage()
                err.ParseFromString(HDDSResp.serializedBody)
                self.log.warning("Got error message from HDDS: %s" % err.error_description)
            elif response.name == "":
                self.log.warning("Set failed: No response from HDDS")
            else:
                self.log.warning("Unexpected response from HDDS: %s" % HDDSResp.name)