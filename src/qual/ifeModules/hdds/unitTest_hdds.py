import unittest
import hdds
from common.gpb.python.HDDS_pb2 import HostDomainDeviceServiceRequest
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

#  @cond doxygen_unittest

## HDDS for IFE Messages
class IFEHDDSMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "HDDS for IFE"

    @staticmethod
    def getMenuItems():
        return [("Get voltage",     IFEHDDSMessages.getVolt),
                ("Get temperature", IFEHDDSMessages.getTemp)]

    @staticmethod
    def getTemp():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        message.key = "ife.temperature.U15_TINT"
        return message

    @staticmethod
    def getVolt():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        message.key = "ife.voltage.U130_3V3"
        return message


## HDDS for IFE Unit Test
class Test_IFEHDDS(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the HDDS test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test HDDS-IFE')
        cls.log.info('++++ Setup before HDDS-IFE module unit tests ++++')
        # Create the module
        cls.module = hdds.IFEHDDS()
        # Uncomment this if you want to see module debug messages
        #cls.module.log.setLevel("DEBUG")

    ## Test case: Test temperature key requests:
    #       success == True
    #       key     == "ife.temperature.U15_TINT"
    #       value   != ""
    def test_temp(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get temp ****")
        response = module.msgHandler(ThalesZMQMessage(IFEHDDSMessages.getTemp()))
        self.assertEqual(response.body.success, True)
        self.assertEqual(response.body.key, "ife.temperature.U15_TINT")
        self.assertNotEqual(response.body.value, "")
        log.info("==== Test complete ====")

    ## Test case: Test temperature key requests:
    #       success == True
    #       key     == "ife.voltage.U130_3V3"
    #       value   != ""
    def test_volt(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get volt ****")
        response = module.msgHandler(ThalesZMQMessage(IFEHDDSMessages.getVolt()))
        self.assertEqual(response.body.success, True)
        self.assertEqual(response.body.key, "ife.voltage.U130_3V3")
        self.assertNotEqual(response.body.value, "")
        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
