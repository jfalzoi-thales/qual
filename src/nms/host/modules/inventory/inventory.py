import os.path

from nms.host.pb2.nms_host_api_pb2 import InventoryReq, InventoryResp, FAILURE_TO_OBTAIN_INVENTORY
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.i350.vpd import VPD


## Inventory Module Class
class Inventory(Module):
    ## Constructor
    #  @param   self
    #  @param   config  Configuration for this module instance
    def __init__(self, config = None):
        # Initialize parent class
        super(Inventory, self).__init__(config)

        ## Ethernet device for I350
        self.i350EthernetDev = "ens1f"
        # Load configuration from config file
        self.loadConfig(attributes=("i350EthernetDev",))

        # Determine if device exists; if not, fall back to file mode
        self.ethDevice = self.i350EthernetDev + "0"
        if not os.path.exists("/sys/class/net/%s" % self.ethDevice):
            self.log.warning("Ethernet device %s not found; using TEST_FILE mode" % self.ethDevice)
            self.ethDevice = "TEST_FILE"

        ## Map two-character VPD field names to HDDS field names
        self.vpdToHDDS = {"PN": "part_number",
                          "SN": "serial_number",
                          "EC": "revision",
                          "VP": "manufacturer_pn",
                          "VD": "manufacturing_date",
                          "VN": "manufacturer_name",
                          "VC": "manufacturer_cage"}

        ## VPD parser/builder
        self.vpd = VPD(self.log, self.vpdToHDDS.keys())

        # Add handler to available message handlers
        self.addMsgHandler(InventoryReq, self.handleMsg)

    ## Handles incoming InventoryReq messages
    #
    #  Receives TZMQ request and performs requested action
    #  @param     self
    #  @param     msg       TZMQ format message
    #  @return    a ThalesZMQMessage object containing the response message
    def handleMsg(self, msg):
        response = InventoryResp()
        response.success = self.readAndParseVPD()
        if not response.success:
            self.log.error("Read VPD from I350 device failed")
            response.error.error_code = FAILURE_TO_OBTAIN_INVENTORY
            response.error.error_description = "Unable to read carrier card inventory from device"
        elif len(self.vpd.vpdEntries) == 0:
            self.log.error("No valid VPD data found on I350 device")
            response.error.error_code = FAILURE_TO_OBTAIN_INVENTORY
            response.error.error_description = "No carrier card inventory data found"
        else:
            for key, value in self.vpd.vpdEntries.items():
                valueResp = response.values.add()
                valueResp.success = True
                valueResp.keyValue.key = self.vpdToHDDS[key]
                valueResp.keyValue.value = value

        return ThalesZMQMessage(response)

    ## Reads VPD from EEPROM (or test file) and updates self.vpdEntries
    #  @param  self
    #  @return True on successful read, False on failure
    def readAndParseVPD(self):
        vpdBytes = self.readVPD()
        if vpdBytes is None:
            self.vpd.vpdEntries.clear()
            return False
        if ord(vpdBytes[0]) == 0x82:
            self.vpd.parseVPD(vpdBytes)
        else:
            self.log.debug("VPD area not programmed")
            self.vpd.vpdEntries.clear()
        return True

    ## Reads VPD from kernel (or test file)
    #  @param  self
    #  @return VPD data
    def readVPD(self):
        if self.ethDevice == "TEST_FILE":
            vpdFile = "/tmp/vpd.bin"
        else:
            vpdFile = "/sys/class/net/%s/device/vpd" % self.ethDevice
        self.log.debug("Reading VPD from file %s" % vpdFile)
        try:
            fh = open(vpdFile, "rb")
            vpdBytes = fh.read(256)
            fh.close()
        except IOError:
            self.log.error("Unable to read VPD file")
            return None
        if len(vpdBytes) <= 1:
            self.log.error("Short read from VPD file")
            return None
        return vpdBytes
