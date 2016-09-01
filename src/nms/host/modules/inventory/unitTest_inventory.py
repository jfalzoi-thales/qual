import unittest

from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from inventory import Inventory
from nms.host.pb2.nms_host_api_pb2 import InventoryReq
from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


#  @cond doxygen_unittest

## Inventory Messages
class InventoryMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Carrier Card Inventory"

    @staticmethod
    def getMenuItems():
        return [("Read data", InventoryMessages.readData),]

    @staticmethod
    def readData():
        message = InventoryReq()
        return message


## Inventory Unit Test
class Test_Inventory(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the Inventory test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test Inventory')
        cls.log.info('++++ Setup before Inventory module unit tests ++++')
        # Create the module
        cls.module = Inventory()
        # Uncomment this if you want to see module debug messages
        #cls.module.log.setLevel("DEBUG")

    ## Test case: Read inventory
    # Expect success == True, nonempty list
    def test_Read(self):
        log = self.__class__.log
        module = self.__class__.module

        response = module.msgHandler(ThalesZMQMessage(InventoryMessages.readData()))
        self.assertEqual(response.name, "InventoryResp")
        self.assertEqual(response.body.success, True)
        self.assertGreater(len(response.body.values), 1)
        log.info("==== Test complete ====")


if __name__ == '__main__':
    ConfigurableObject.setFilename("HNMS")
    unittest.main()

## @endcond
