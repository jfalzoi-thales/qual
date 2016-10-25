import unittest
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
        return "VLAN Assignment"

    @staticmethod
    def getMenuItems():
        return [("Set VF1 int 301 ext 127", VlanAssignmentMessages.configVFExtVlanIntVlan),
                ("Set VF1 int 301",         VlanAssignmentMessages.configVFIntVlan),
                ("Set VF1 none",            VlanAssignmentMessages.configVFNoVlans),
                ("Set PF int 301",          VlanAssignmentMessages.configPFIntVlan),
                ("Set PF none",             VlanAssignmentMessages.configPFNoVlans)]

    @staticmethod
    def configPFIntVlan():
        message = VLANAssignReq()
        message.port_name.append('i350_pf_1')
        message.port_name.append('i350_pf_2')
        message.port_name.append('i350_pf_3')
        message.port_name.append('i350_pf_4')
        message.internal_vlans.append(301)
        return message

    @staticmethod
    def configPFNoVlans():
        message = VLANAssignReq()
        message.port_name.append('i350_pf_1')
        message.port_name.append('i350_pf_2')
        message.port_name.append('i350_pf_3')
        message.port_name.append('i350_pf_4')
        return message

    @staticmethod
    def configVFExtVlanIntVlan():
        message = VLANAssignReq()
        message.port_name.append('i350_pf_1_vf1')
        message.port_name.append('i350_pf_2_vf1')
        message.port_name.append('i350_pf_3_vf1')
        message.port_name.append('i350_pf_4_vf1')
        message.external_vlans.append(127)
        message.internal_vlans.append(301)
        return message

    @staticmethod
    def configVFIntVlan():
        message = VLANAssignReq()
        message.port_name.append('i350_pf_1_vf1')
        message.port_name.append('i350_pf_2_vf1')
        message.port_name.append('i350_pf_3_vf1')
        message.port_name.append('i350_pf_4_vf1')
        message.internal_vlans.append(301)
        return message

    @staticmethod
    def configVFNoVlans():
        message = VLANAssignReq()
        message.port_name.append('i350_pf_1_vf1')
        message.port_name.append('i350_pf_2_vf1')
        message.port_name.append('i350_pf_3_vf1')
        message.port_name.append('i350_pf_4_vf1')
        return message

    @staticmethod
    def configNoPort():
        message = VLANAssignReq()
        return message

    @staticmethod
    def configBadPort1():
        message = VLANAssignReq()
        message.port_name.append('i351_pf_1_vf1')
        return message

    @staticmethod
    def configBadPort2():
        message = VLANAssignReq()
        message.port_name.append('i350_pf_5_vf1')
        return message

    @staticmethod
    def configBadPort3():
        message = VLANAssignReq()
        message.port_name.append('i350_pf_1_vf8')
        return message

    @staticmethod
    def configBadPort4():
        message = VLANAssignReq()
        message.port_name.append('i350_pf_1_vf1_vf1')
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
        cls.log.info("++++ Teardown after VLAN Assignment module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        log.info("==== Reset module state ====")

    ## Valid Test case
    #
    #   Send a sequence of valid messages
    def test_validSequence(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Valid VLAN message sequence ****")

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configVFIntVlan()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, True)

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configVFExtVlanIntVlan()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, True)

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configVFIntVlan()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, True)

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configVFNoVlans()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, True)

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configPFIntVlan()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, True)

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configPFNoVlans()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, True)

        log.info("==== Test complete ====")

    ## Fail Test case
    #
    #   Send a noPort message
    def test_noPort(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: no port_name in message ****")

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configNoPort()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ERROR_PROCESSING_MESSAGE)

        log.info("==== Test complete ====")

    ## Fail Test case
    #
    #   Send badPort messages
    def test_badPort(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test cases: Various bad port names ****")

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configBadPort1()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ERROR_PROCESSING_MESSAGE)

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configBadPort2()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ERROR_PROCESSING_MESSAGE)

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configBadPort3()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ERROR_PROCESSING_MESSAGE)

        response = module.msgHandler(ThalesZMQMessage(VlanAssignmentMessages.configBadPort4()))
        self.assertEqual(response.name, "VLANAssignResp")
        self.assertEqual(response.body.success, False)
        self.assertEqual(response.body.error.error_code, ERROR_PROCESSING_MESSAGE)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
