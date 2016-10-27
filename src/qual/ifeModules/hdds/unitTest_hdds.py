import unittest

import hdds
from qual.pb2.HDDS_pb2 import HostDomainDeviceServiceRequest
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


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

    @staticmethod
    def getBogusTemp():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        message.key = "ife.temperature.bogusTemp"
        return message

    @staticmethod
    def getBogusVolt():
        message = HostDomainDeviceServiceRequest()
        message.requestType = HostDomainDeviceServiceRequest.GET
        message.key = "ife.voltage.bogusVolt"
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

    ## Test case: Test bogus temperature and voltage keys:
    #       success == False
    #       key     == "ife.temperature.bogusTemp"
    #       value   == ""
    #       ---------------------
    #       success == False
    #       key     == "ife.voltage.bogusVolt"
    #       value   == ""
    #       ---------------------
    def test_bogus(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Get bogus temp ****")
        response = module.msgHandler(ThalesZMQMessage(IFEHDDSMessages.getBogusTemp()))
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.key, "ife.temperature.bogusTemp")
        self.assertEqual(response.body.value, "")

        log.info("**** Test case: Get bogus volt ****")
        response = module.msgHandler(ThalesZMQMessage(IFEHDDSMessages.getBogusVolt()))
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.key, "ife.voltage.bogusVolt")
        self.assertEqual(response.body.value, "")
        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
