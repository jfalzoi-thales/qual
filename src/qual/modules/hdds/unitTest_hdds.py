import unittest
import hdds
from common.gpb.python.HDDS_API_pb2 import GetReq, SetReq, FAILURE_INVALID_KEY
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

#  @cond doxygen_unittest

## HDDS Messages
class HDDSMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "HDDS"

    @staticmethod
    def getMenuItems():
        return [("Get single value",     HDDSMessages.getSingle),
                ("Get multiple values",  HDDSMessages.getMultiple),
                ("Set single value",     HDDSMessages.setSingle)]

    @staticmethod
    def getSingle():
        message = GetReq()
        message.key.append("external_pins.output.pin_a6")
        return message

    @staticmethod
    def getMultiple():
        message = GetReq()
        message.key.append("external_pins.output.pin_a6")
        message.key.append("external_pins.output.pin_b6")
        message.key.append("external_pins.output.pin_c6")
        return message

    @staticmethod
    def setSingle():
        message = SetReq()
        prop = message.values.add()
        prop.key = "external_pins.output.pin_a6"
        prop.value = "HIGH"
        return message

    @staticmethod
    def getBogus():
        message = GetReq()
        message.key.append("bogus_key")
        return message

    @staticmethod
    def setBogus():
        message = SetReq()
        prop = message.values.add()
        prop.key = "bogus_key"
        prop.value = "x"
        return message


## HDDS Unit Test
class Test_HDDS(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the HDDS test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test HDDS')
        cls.log.info('++++ Setup before HDDS module unit tests ++++')
        # Create the module
        cls.module = hdds.HDDS()
        # Uncomment this if you want to see module debug messages
        #cls.module.log.setLevel("DEBUG")

    ## Test case: Try to get an invalid key
    # Should return a GetResp with success=False, error_code=FAILURE_INVALID_KEY
    def test_getInvalidKey(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get invalid key ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.getBogus()))
        self.assertEqual(response.name, "GetResp")
        self.assertEqual(len(response.body.values), 1)
        self.assertEqual(response.body.values[0].success, False)
        self.assertEqual(response.body.values[0].error.error_code, FAILURE_INVALID_KEY)
        log.info("==== Test complete ====")

    ## Test case: Try to set an invalid key
    # Should return a SetResp with success=False, error_code=FAILURE_INVALID_KEY
    def test_setInvalidKey(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Set invalid key ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.setBogus()))
        self.assertEqual(response.name, "SetResp")
        self.assertEqual(len(response.body.values), 1)
        self.assertEqual(response.body.values[0].success, False)
        self.assertEqual(response.body.values[0].error.error_code, FAILURE_INVALID_KEY)
        log.info("==== Test complete ====")

    ## Test case: Try to get a single value
    # Should return a GetResp with success=true and nonempty value
    def test_getSingle(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get single ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.getSingle()))
        self.assertEqual(response.name, "GetResp")
        self.assertEqual(len(response.body.values), 1)
        self.assertEqual(response.body.values[0].success, True)
        self.assertEqual(response.body.values[0].keyValue.key, "external_pins.output.pin_a6")
        self.assertNotEqual(response.body.values[0].keyValue.value, "")
        log.info("==== Test complete ====")

    ## Test case: Try to set a single value
    # Should return a SetResp with GetResp with success=true and value equal to what we set
    def test_setSingle(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Set value ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.setSingle()))
        self.assertEqual(response.name, "SetResp")
        self.assertEqual(len(response.body.values), 1)
        self.assertEqual(response.body.values[0].success, True)
        self.assertEqual(response.body.values[0].keyValue.key, "external_pins.output.pin_a6")
        self.assertEqual(response.body.values[0].keyValue.value, "HIGH")

    ## Test case: Try to get multiple values
    # Should return a GetResp with success=true for each value
    def test_getMultiple(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get multiple ****")
        response = module.msgHandler(ThalesZMQMessage(HDDSMessages.getMultiple()))
        self.assertEqual(response.name, "GetResp")
        self.assertEqual(len(response.body.values), 3)
        self.assertEqual(response.body.values[0].success, True)
        self.assertEqual(response.body.values[1].success, True)
        self.assertEqual(response.body.values[2].success, True)
        log.info("==== Test complete ====")


if __name__ == '__main__':
    unittest.main()

## @endcond