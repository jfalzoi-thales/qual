import unittest
import time
from nms.host.pb2.nms_host_api_pb2 import *
from nms.host.modules.vlanassignment.vlanAssignment import VlanAssignment
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## VLAN Assignment Messages
#
class VlanAssignmentMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Config Port State"

    @staticmethod
    def getMenuItems():
        return [("Send BLOCKING", VlanAssignmentMessages.send_1portName_1ExtVlan_1IntVlan)]

    @staticmethod
    def send_1portName_1ExtVlan_1IntVlan():
        message = VLANAssignReq()
        message.port_name.append('internal.switch_2')
        message.external_vlans.append(1)
        message.internal_vlans.append(2)
        return message

    @staticmethod
    def send_0portName_0ExtVlan_0IntVlan():
        message = VLANAssignReq()
        return message

## VLAN Assignment Unit Test
class Test_VlanAssig(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the VLAN Assignment test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test VLAN Assignment')
        cls.log.info('++++ Setup before VLAN Assignment module unit tests ++++')
        # Create the module
        cls.module = VlanAssignment()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with Config Port State test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after Config Port State module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")

    ## Valid Test case
    #
    #   Send a 1portName_1ExtVlan_1IntVlan Message
    def test_1portName_1ExtVlan_1IntVlan(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: 1portName_1ExtVlan_1IntVlan message ****")
        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.send_1portName_1ExtVlan_1IntVlan()))

        # Asserts
        self.assertEqual(response.body.success, True)

        log.info("==== Test complete ====")

    ## Fail Test case
    #
    #   Send a 0portName_0ExtVlan_0IntVlan Message
    def test_0portName_0ExtVlan_0IntVlan(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: 1portName_1ExtVlan_1IntVlan message ****")
        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.send_0portName_0ExtVlan_0IntVlan()))

        # Asserts
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, 1002)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
