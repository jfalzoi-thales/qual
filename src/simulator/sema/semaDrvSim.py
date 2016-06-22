
from common.logger import logger
from common.tzmq.ThalesZMQServer import ThalesZMQServer
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.gpb.python.SEMA_pb2 import RequestStatusMessage, ResponseStatusMessage


## SEMA Driver Simulator class
#
# Implements a subset of the SEMA Driver service, as specified
# in the "MPS Smart Embedded Management Agent Driver (SEMA) ICD".
# Specifically, it implements the RequestStatusMessage message, with
# the following limitations:
#   - Values read will always be the same
#
# The SEMA Driver ZMQ service uses IPC at ipc:///tmp/sema-drv.sock
# per the "MAP Network Configuration" document.
#
class SEMADriverSimulator(ThalesZMQServer):
    def __init__(self):
        super(SEMADriverSimulator, self).__init__("ipc:///tmp/sema-drv.sock")

        # Turn down ThalesZMQServer debug level
        self.log.setLevel(logger.INFO)

        # List of properties that can be retrieved.
        # Taken from the "Logical Name" table in the document
        # "MPS Smart Embedded Management Agent Driver (SEMA) ICD".
        self.properties = {"BIOSIndex":         "0",
                           "BIOSVersion":       "1.2.3",
                           "BoardHWRevision":   "2",
                           "BoardManufacturer": "Foxconn",
                           "BoardMaxTemp":      "55.5",
                           "BoardMinTemp":      "22.2",
                           "BoardName":         "Zaphod",
                           "BoardTemp":         "33.3",
                           "BootCount":         "42",
                           "BootVersion":       "2.1",
                           "ChipsetID":         "Potato",
                           "CPUMaxTemp":        "66.7",
                           "CPUMinTemp":        "22.3",
                           "CPUTemp":           "44.5",
                           "MainPowerCurrent":  "1.1",
                           "PowerConsumption":  "234.5",
                           "PwrCycles":         "89",
                           "PwrUpTime":         "5678",
                           "RestartEvent":      "PowerCycle",
                           "SerialNumber":      "7654",
                           "TotalUpTime":       "67890",
                           "Voltage_3V3S":      "3.2",
                           "Voltage_1V05S":     "1.04",
                           "Voltage_3V3A":      "3.1",
                           "Voltage_1V5":       "1.4",
                           "Voltage_5V":        "4.9",
                           "Voltage_12V":       "11.9"}

    ## Called by base class when a request is received from a client.
    #
    # @param request ThalesZMQMessage object containing received request
    #
    def handleRequest(self, request):
        if request.name == "RequestStatusMessage":
            # Parse request message
            requestMsg = RequestStatusMessage()
            requestMsg.ParseFromString(request.serializedBody)

            # Create a SEMA response message for the results
            responseMsg = ResponseStatusMessage()
            responseMsg.name = requestMsg.name

            # Look up the name
            if requestMsg.name in self.properties:
                responseMsg.error = ResponseStatusMessage.STATUS_OK
                responseMsg.value = self.properties[requestMsg.name]
            else:
                print "Request for unknown item:", requestMsg.name
                responseMsg.error = ResponseStatusMessage.STATUS_INVALID_NAME

            # Send response back to client
            return ThalesZMQMessage(responseMsg)

        else:
            print "Error! Unknown request type"
            # Send "Unsupported Message" error back to client
            return self.getUnsupportedMessageErrorResponse()


if __name__ == "__main__":
    simulator = SEMADriverSimulator()
    simulator.run()
    print "Exit SEMA Driver simulator"
