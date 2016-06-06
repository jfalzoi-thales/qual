import os
from common.gpb.python.SystemMonitoring_pb2 import SystemMonitoringRequest, SystemMonitoringResponse
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.PowerInfo_pb2 import GetPowerInfo, PowerInfo
from common.gpb.python.SEMA_pb2 import RequestStatusMessage, ResponseMessage
from common.module import module

## SystemMonitoring Module
class SystemMonitoring(module.Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config = {}):
        ## initializes parent class
        super(SystemMonitoring, self).__init__({})
        ## adds handler to available message handlers
        self.addMsgHandler(SystemMonitoringRequest, self.handler)
        #  Ensure directories for communication with simulators are present
        pwripcdir = "tmp/pwr-supp-mon.sock"
        semaipcdir = "tmp/sema-drv.sock"

        if not os.path.exists(pwripcdir):
            os.makedirs(pwripcdir)
        if not os.path.exists(semaipcdir):
            os.makedirs(semaipcdir)

        ## Connection to PowerInfo driver
        self.pwrClient = ThalesZMQClient("ipc:///tmp/pwr-supp-mon.sock")
        ## Connection to SEMA driver
        self.semaClient = ThalesZMQClient("ipc:///tmp/sema-drv.sock")

    ## Sends GetPowerInfo request message to the PowerInfo driver
    #  @param   self
    #  @param   response    SystemMonitoringResponse object
    def makePwrRequest(self, response):
        pwrInfo = PowerInfo()
        #  Sends a GetPowerInfo() request to driver which returns a tzmq message that is deserialized into pwrInfo
        pwrInfo.ParseFromString(self.pwrClient.sendRequest(ThalesZMQMessage(GetPowerInfo())).serializedBody)

        for value in pwrInfo.values:
            sensor = response.powerSupplyStatistics.add()
            sensor.deviceName = value.name
            sensor.sensorName = value.key
            sensor.value = value.value

    ## Sends RequestStatusMessage request message to the SEMA driver
    #  @param   self
    #  @param   response    SystemMonitoringResponse object
    def makeSEMARequest(self, response):
        #  Hardcoded to function with our simulator; needs more details to implement with real peripheral
        properties = ["BIOSIndex", "BIOSVersion", "BoardHWRevision", "BoardManufacturer", "BoardMaxTemp", "BoardMinTemp", "BoardName", "BoardTemp", "BootCount", "BootVersion", "ChipsetID", "CPUMaxTemp", "CPUMinTemp", "CPUTemp", "MainPowerCurrent", "PowerConsumption", "PwrCycles", "PwrUpTime", "RestartEvent", "SerialNumber", "TotalUpTime", "Voltage_3V3S", "Voltage_1V05S", "Voltage_3V3A", "Voltage_1V5", "Voltage_5V", "Voltage_12V"]
        semaInfo = ResponseMessage()

        for property in properties:
            request = RequestStatusMessage()
            request.name = property
            #  Sends a RequestStatusMessage() request to driver which returns a tzmq message that is deserialized into semaInfo
            semaInfo.ParseFromString(self.semaClient.sendRequest(ThalesZMQMessage(request)).serializedBody)

            if semaInfo.error == ResponseMessage.OK:
                sema = response.semaStatistics.add()
                sema.itemName = semaInfo.name
                sema.value = semaInfo.value
            else:
                self.log.error("Property ERROR CODE: %d" % (semaInfo.error))

    ## Sends request message to the ??? driver
    #  TODO: Update once port temperature simulator is available
    #  @param   self
    #  @param   response    SystemMonitoringResponse object
    def makePortRequest(self, response):
        return

    ## Handles incoming tzmq messages
    #  @param     self
    #  @param     msg   tzmq format message
    #  @return    ThalesZMQMessage object
    def handler(self, msg):
        response = SystemMonitoringResponse()
        self.makePwrRequest(response)
        self.makeSEMARequest(response)
        #  Temporary values until simulator is available
        response.switchData.temperature = "10,000,000 degrees"
        response.switchData.statistics.append("SUPER SECRET STATISTICS")

        return ThalesZMQMessage(response)