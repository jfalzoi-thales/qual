from common.gpb.python.SystemMonitoring_pb2 import SystemMonitoringRequest, SystemMonitoringResponse
from common.tzmq.ThalesZMQClient import ThalesZMQClient
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.PowerInfo_pb2 import GetPowerInfo, PowerInfo
from common.gpb.python.SEMA_pb2 import RequestStatusMessage, ResponseStatusMessage
from common.module import module

## SystemMonitoring Module
class SystemMonitoring(module.Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config = None):
        super(SystemMonitoring, self).__init__(config)
        ## Connection to PowerInfo driver
        self.pwrClient = ThalesZMQClient("ipc:///tmp/pwr-supp-mon.sock", log=self.log, msgParts=2)
        ## Connection to SEMA driver
        self.semaClient = ThalesZMQClient("ipc:///tmp/sema-drv.sock", log=self.log, msgParts=2)
        ## Peripheral statistics to retrieve from SEMA driver
        self.semaProperties = ["BIOSIndex", "BIOSVersion", "BoardHWRevision", "BoardManufacturer", "BoardMaxTemp",
                               "BoardMinTemp", "BoardName", "BoardTemp", "BootCount", "BootVersion", "ChipsetID",
                               "CPUMaxTemp", "CPUMinTemp", "CPUTemp", "MainPowerCurrent", "PowerConsumption",
                               "PwrCycles",
                               "PwrUpTime", "RestartEvent", "SerialNumber", "TotalUpTime", "Voltage_3V3S",
                               "Voltage_1V05S",
                               "Voltage_3V3A", "Voltage_1V5", "Voltage_5V", "Voltage_12V"]
        #  Adds handler to available message handlers
        self.addMsgHandler(SystemMonitoringRequest, self.handler)

    ## Sends GetPowerInfo request message to the PowerInfo driver
    #  @param   self
    #  @param   response    SystemMonitoringResponse object
    def makePwrRequest(self, response):
        pwrInfo = PowerInfo()
        #  Sends a GetPowerInfo() request to driver which returns a tzmq message that is deserialized into pwrInfo
        reply = self.pwrClient.sendRequest(ThalesZMQMessage(GetPowerInfo()))
        if reply.name == "PowerInfo":
            pwrInfo.ParseFromString(reply.serializedBody)
            for value in pwrInfo.values:
                sensor = response.powerSupplyStatistics.add()
                sensor.deviceName = value.name
                sensor.sensorName = value.key
                sensor.value = value.value

    ## Sends RequestStatusMessage request message to the SEMA driver
    #  @param   self
    #  @param   response    SystemMonitoringResponse object
    def makeSEMARequest(self, response):
        semaInfo = ResponseStatusMessage()

        failCount = 0
        for prop in self.semaProperties:
            request = RequestStatusMessage()
            request.name = prop
            #  Override the message name, because SEMA driver doesn't use the GPB message name
            message = ThalesZMQMessage(request)
            message.name = "Status"
            #  Sends a RequestStatusMessage() request to driver which returns a tzmq message that is deserialized into semaInfo
            reply = self.semaClient.sendRequest(message)
            if reply.name == "Status":
                semaInfo.ParseFromString(reply.serializedBody)
                if semaInfo.error == ResponseStatusMessage.STATUS_OK:
                    sema = response.semaStatistics.add()
                    sema.itemName = semaInfo.name
                    sema.value = semaInfo.value
                else:
                    self.log.error("Property ERROR CODE: %d" % (semaInfo.error))
            elif reply.name == "":
                # Communication error; break out of loop after a few failures
                failCount += 1
                if failCount >= 3:
                    self.log.error("Failed to contact SEMA driver %d times; giving up" % failCount)
                    break

    ## Sends request message to the Network Management Service
    #  @todo    Update once Network Management Service is available
    #  @param   self
    #  @param   response    SystemMonitoringResponse object
    def makeNetworkMgmtRequest(self, response):
        #  Temporary values until Network Management Service is available
        response.switchData.temperature = "10,000,000 degrees"
        response.switchData.statistics.append("SUPER SECRET STATISTICS")

    ## Handles incoming tzmq messages
    #  @param     self
    #  @param     msg   tzmq format message
    #  @return    ThalesZMQMessage object
    def handler(self, msg):
        response = SystemMonitoringResponse()
        self.makePwrRequest(response)
        self.makeSEMARequest(response)
        self.makeNetworkMgmtRequest(response)

        return ThalesZMQMessage(response)
