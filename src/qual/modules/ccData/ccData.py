from qual.pb2.CarrierCardData_pb2 import CarrierCardDataRequest, CarrierCardDataResponse, ErrorMsg
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from i350Inventory import I350Inventory


## CarrierCardData Module Class
class CarrierCardData(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        # Initialize parent class
        super(CarrierCardData, self).__init__(config)

        ## Length limits, indexed by HDDS key
        self.lengthLimits = {"part_number":        24,
                             "serial_number":      24,
                             "revision":           8,
                             "manufacturer_pn":    24,
                             "manufacturing_date": 8,
                             "manufacturer_name":  24,
                             "manufacturer_cage":  8}


        ## Object for accessing inventory on I350 device
        self.i350Inventory = I350Inventory(self.log)

        # Add handler to available message handlers
        self.addMsgHandler(CarrierCardDataRequest, self.handleMsg)

    ## Handles incoming CarrierCardDataRequest messages
    #
    #  Receives TZMQ request and performs requested action
    #  @param     self
    #  @param     msg       TZMQ format message
    #  @return    a ThalesZMQMessage object containing the response message
    def handleMsg(self, msg):
        response = CarrierCardDataResponse()

        if msg.body.requestType == CarrierCardDataRequest.READ:
            self.handleRead(response)
        elif msg.body.requestType == CarrierCardDataRequest.WRITE:
            self.handleWrite(msg.body, response)
        elif msg.body.requestType == CarrierCardDataRequest.ERASE:
            self.handleErase(response)
        elif msg.body.requestType == CarrierCardDataRequest.WRITE_PROTECT:
            self.handleWriteProtect(response)
        else:
            self.log.error("Unexpected Request Type %d" % msg.body.requestType)
            response.success = False
            response.error.error_code = ErrorMsg.FAILURE_INVALID_MESSAGE
            response.error.description = "Invalid Request Type"

        return ThalesZMQMessage(response)

    ## Handles requests with requestType of READ
    #  @param    self
    #  @param    response    CarrierCardDataResponse object
    def handleRead(self, response):
        values = self.i350Inventory.read()
        if values is None:
            response.success = False
            response.error.error_code = ErrorMsg.FAILURE_READ_FAILED
            response.error.description = "Read inventory failed"
            return

        response.success = True
        response.writeProtected = self.i350Inventory.getWriteProtectFlag()
        for key, value in values.items():
            kv = response.values.add()
            kv.key = key
            kv.value = value

    ## Handles requests with requestType of WRITE
    #  @param    self
    #  @param    request     Message body with request details
    #  @param    response    CarrierCardDataResponse object
    def handleWrite(self, request, response):
        values = {}
        # Validate supplied entries
        for kv in request.values:
            shortKey = kv.key.split(".")[1]
            if shortKey not in self.lengthLimits:
                self.log.warning("Attempt to write invalid key %s" % kv.key)
                response.success = False
                response.error.error_code = ErrorMsg.FAILURE_INVALID_KEY
                response.error.description = "Invalid key: %s" % kv.key
                return
            elif len(kv.value) == 0 or len(kv.value) > self.lengthLimits[shortKey]:
                self.log.warning("Attempt to write invalid value for key %s" % kv.key)
                response.success = False
                response.error.error_code = ErrorMsg.FAILURE_INVALID_VALUE
                response.error.description = "Invalid value for key: %s" % kv.key
                return
            else:
                values[kv.key] = kv.value

        # Update the inventory with new values
        response.success, msg = self.i350Inventory.update(values)
        if not response.success:
            response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
            response.error.description = msg
            return

        # Return all current entries in response
        values = self.i350Inventory.read()
        if values is not None:
            for key, value in values.items():
                kv = response.values.add()
                kv.key = key
                kv.value = value

    ## Handles requests with requestType of ERASE
    #  @param    self
    #  @param    response    CarrierCardDataResponse object
    def handleErase(self, response):
        response.success, msg = self.i350Inventory.erase()
        if not response.success:
            response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
            response.error.description = msg

    ## Handles requests with requestType of WRITE_PROTECT
    #  @param    self
    #  @param    response    CarrierCardDataResponse object
    def handleWriteProtect(self, response):
        response.success, msg = self.i350Inventory.writeProtect()
        if not response.success:
            response.error.error_code = ErrorMsg.FAILURE_WRITE_FAILED
            response.error.description = msg
            return

        # Successful, so now we can set the writeProtected flag in the response
        response.writeProtected = True

    ## Cleans up
    #  @param     self
    def terminate(self):
        self.i350Inventory.cleanup()
