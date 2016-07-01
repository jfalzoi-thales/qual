import unittest
from time import sleep
import ccData
from common.gpb.python.CarrierCardData_pb2 import CarrierCardDataRequest, ErrorMsg
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

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
        kv.key   = "part_number"
        kv.value = "TH-CC-ABC12345"
        kv = message.values.add()
        kv.key   = "serial_number"
        kv.value = "000000123456789"
        kv = message.values.add()
        kv.key   = "revision"
        kv.value = "27B-6"
        kv = message.values.add()
        kv.key   = "manufacturer_pn"
        kv.value = "TKL-9876543"
        kv = message.values.add()
        kv.key   = "manufacturing_date"
        kv.value = "20160630"
        kv = message.values.add()
        kv.key   = "manufacturer_name"
        kv.value = "tkLABS"
        kv = message.values.add()
        kv.key   = "manufacturer_cage"
        kv.value = "1234"
        return message

    @staticmethod
    def writePartial():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE
        kv = message.values.add()
        kv.key   = "part_number"
        kv.value = "ABC-11111"
        kv = message.values.add()
        kv.key   = "serial_number"
        kv.value = "S55555555555"
        kv = message.values.add()
        kv.key   = "revision"
        kv.value = "A"
        return message

    @staticmethod
    def writeBadKey():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE
        kv = message.values.add()
        kv.key   = "bogus_number"
        kv.value = "ABC-11111"
        return message

    @staticmethod
    def writeEmptyValue():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE
        kv = message.values.add()
        kv.key   = "part_number"
        kv.value = ""
        return message

    @staticmethod
    def writeLongValue():
        message = CarrierCardDataRequest()
        message.requestType = CarrierCardDataRequest.WRITE
        kv = message.values.add()
        kv.key   = "part_number"
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
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test CarrierCardData')
        cls.log.info('++++ Setup before CarrierCardData module unit tests ++++')
        # Create the module
        cls.module = ccData.CarrierCardData()
        # Uncomment this if you want to see module debug messages
        #cls.module.log.setLevel("DEBUG")

    ## Test case: Send a WRITE message with invalid key
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
    def test_WriteLongValue(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: WRITE message - value too long ****")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeLongValue()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ErrorMsg.FAILURE_INVALID_VALUE)
        log.info("==== Test complete ====")

    ## Test case: Send a READ message
    def ztest_Read(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: READ message ****")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.readData()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        log.info("==== Test complete ====")

    ## Test case: Send a WRITE message
    def test_Write(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: WRITE message ****")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.writeFull()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 7)
        log.info("==== Test complete ====")

    ## Test case: Send an ERASE message
    def test_Erase(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: ERASE message ****")
        response = module.msgHandler(ThalesZMQMessage(CarrierCardDataMessages.eraseData()))
        self.assertEqual(response.name, "CarrierCardDataResponse")
        self.assertEqual(response.body.success, True)
        self.assertEqual(len(response.body.values), 0)
        log.info("==== Test complete ====")


if __name__ == '__main__':
    unittest.main()

## @endcond
