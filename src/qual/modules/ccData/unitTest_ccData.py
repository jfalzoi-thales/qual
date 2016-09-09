import unittest

import ccData
from qual.pb2.CarrierCardData_pb2 import CarrierCardDataRequest, ErrorMsg
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


#  @cond doxygen_unittest

## CarrierCardData Messages
class CarrierCardDataMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Carrier Card Data"

    @staticmethod
    def getMenuItems():
        return [("Read data",          CarrierCardDataMessages.readData),
                ("Write full data",    CarrierCardDataMessages.writeFull),
                ("Write partial data", CarrierCardDataMessages.writePartial),
                ("Erase data",         CarrierCardDataMessages.eraseData),
                ("Write protect",      CarrierCardDataMessages.writeProtect)]

    @staticmethod
    def readData():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.READ
        return message

    @staticmethod
    def writeFull():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE
        kv = message.values.add()
        kv.key   = "carrier_card.part_number"
        kv.value = "TH-CC-ABC12345"
        kv = message.values.add()
        kv.key   = "carrier_card.serial_number"
        kv.value = "000000123456789"
        kv = message.values.add()
        kv.key   = "carrier_card.revision"
        kv.value = "27B-6"
        kv = message.values.add()
        kv.key   = "carrier_card.manufacturer_pn"
        kv.value = "TKL-9876543"
        kv = message.values.add()
        kv.key   = "carrier_card.manufacturing_date"
        kv.value = "20160630"
        kv = message.values.add()
        kv.key   = "carrier_card.manufacturer_name"
        kv.value = "tkLABS"
        kv = message.values.add()
        kv.key   = "carrier_card.manufacturer_cage"
        kv.value = "1234"
        return message

    @staticmethod
    def writePartial():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE
        kv = message.values.add()
        kv.key   = "carrier_card.part_number"
        kv.value = "ABC-11111"
        kv = message.values.add()
        kv.key   = "carrier_card.serial_number"
        kv.value = "S55555555555"
        kv = message.values.add()
        kv.key   = "carrier_card.revision"
        kv.value = "A"
        return message

    @staticmethod
    def writeIncomplete():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE
        kv = message.values.add()
        kv.key   = "carrier_card.part_number"
        kv.value = "ABC-22222"
        kv = message.values.add()
        kv.key   = "carrier_card.manufacturer_pn"
        kv.value = "TKL-9876543"
        kv = message.values.add()
        kv.key   = "carrier_card.manufacturing_date"
        kv.value = "20160630"
        return message

    @staticmethod
    def writeBadKey():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE
        kv = message.values.add()
        kv.key   = "carrier_card.bogus_number"
        kv.value = "ABC-11111"
        return message

    @staticmethod
    def writeEmptyValue():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE
        kv = message.values.add()
        kv.key   = "carrier_card.part_number"
        kv.value = ""
        return message

    @staticmethod
    def writeLongValue():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE
        kv = message.values.add()
        kv.key   = "carrier_card.part_number"
        kv.value = "1234567890123456789012345"
        return message

    @staticmethod
    def eraseData():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.ERASE
        return message

    @staticmethod
    def writeProtect():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE_PROTECT
        return message


## CarrierCardData Unit Test
class Test_CarrierCardData(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the CarrierCardData test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test CarrierCardData')
        cls.log.info('++++ Setup before CarrierCardData module unit tests ++++')
        # Create the module
        cls.module = ccData.CarrierCardData()
        # Uncomment this if you want to see module debug messages
        #cls.module.log.setLevel("DEBUG")

    ## Teardown when done with CarrierCardData test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after CarrierCardData module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        # Clear write protection in simulated mode
        if module.i350Inventory.ethDevice == "TEST_FILE":
            module.i350Inventory.resetProtectionTestFile()

    ## Test case: Send a WRITE message with invalid key
    # Expect failure with FAILURE_INVALID_KEY
    def test_WriteBadKey(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: WRITE message - invalid key ****")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeBadKey()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ErrorMsg.FAILURE_INVALID_KEY)
        log.info("==== Test complete ====")

    ## Test case: Send a WRITE message with an empty value
    # Expect failure with FAILURE_INVALID_VALUE
    def test_WriteEmptyValue(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: WRITE message - empty value ****")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeEmptyValue()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ErrorMsg.FAILURE_INVALID_VALUE)
        log.info("==== Test complete ====")

    ## Test case: Send a WRITE message with a value that exceeds the length limit
    # Expect failure with FAILURE_INVALID_VALUE
    def test_WriteLongValue(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: WRITE message - value too long ****")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeLongValue()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ErrorMsg.FAILURE_INVALID_VALUE)
        log.info("==== Test complete ====")

    ## Test case: Send sequence: ERASE, READ, WRITE, READ
    # Expect empty value list after erase, populated value list after write
    def test_EraseWriteRead(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: ERASE,READ,WRITE,READ sequence ****")
        log.info("==== Erase data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.eraseData()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 0)

        log.info("==== Read data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.readData()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 0)

        log.info("==== Write data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeFull()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 7)

        log.info("==== Read data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.readData()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 7)
        log.info("==== Test complete ====")

    ## Test case: Send two WRITE sequences, second augmenting the first
    # Expect 2 values after first write, 4 values after second write
    def test_WritePartials(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Augmenting WRITE messages ****")
        log.info("==== Erase data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.eraseData()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 0)

        log.info("==== Write data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writePartial()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 3)

        log.info("==== Write more data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeIncomplete()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 5)

        log.info("==== Read data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.readData()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 5)
        log.info("==== Test complete ====")

    ## Test case: Test various scenarios related to the WRITE_PROTECT message
    # Only executed in TEST_FILE mode, not on real hardware
    # WARNING: Manipulates module instance variable "enableWriteProtect" directly
    # Expect:
    #   When enableWriteProtect is False, write protect fails with FAILURE_WRITE_PROTECT_DISABLED
    #   When required data has not been programmed, write protect fails with FAILURE_INVALID_VALUE
    #   When required data has been programmed, write protect succeeds
    #   When write protect is enabled, read reports writeProtected = True
    #   When write protect is enabled, second write protect succeeds
    #   When write protect is enabled, write and erase fail with FAILURE_WRITE_FAILED
    def test_WriteProtect(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: WRITE_PROTECT message ****")
        if module.i350Inventory.ethDevice != "TEST_FILE":
            log.info("==== Not executing because module is not configured for test file mode ===")
            return

        log.info("==== Protect when enableWriteProtect is False ====")
        module.i350Inventory.enableWriteProtect = False
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeProtect()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ErrorMsg.FAILURE_WRITE_FAILED)

        # Enable write protect function for remaining tests
        module.i350Inventory.enableWriteProtect = True

        log.info("==== Erase data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.eraseData()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 0)

        log.info("==== Write incomplete data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeIncomplete()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)

        log.info("==== Protect when required data is missing ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeProtect()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ErrorMsg.FAILURE_WRITE_FAILED)

        log.info("==== Write additional data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeFull()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)

        log.info("==== Protect when required data is present ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeProtect()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(response.body.writeProtected, True)

        log.info("==== Read data ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.readData()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(response.body.writeProtected, True)

        log.info("==== Protect when already protected ====")
        module.i350Inventory.enableWriteProtect = True
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeProtect()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(response.body.writeProtected, True)

        log.info("==== Write data when protected ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writePartial()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ErrorMsg.FAILURE_WRITE_FAILED)

        log.info("==== Erase data when protected ====")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.eraseData()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ErrorMsg.FAILURE_WRITE_FAILED)

        log.info("==== Test complete ====")


if __name__ == '__main__':
    unittest.main()

## @endcond
