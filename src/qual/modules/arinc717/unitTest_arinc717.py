import unittest

import arinc717
from qual.pb2.ARINC717Frame_pb2 import ARINC717FrameRequest, ARINC717FrameResponse
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger import logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


#  @cond doxygen_unittest

## ARINC717 Messages
class ARINC717Messages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "ARINC 717"

    @staticmethod
    def getMenuItems():
        return [("Report",  ARINC717Messages.report),]

    @staticmethod
    def report():
        message = ARINC717FrameRequest()
        message.requestType = ARINC717FrameRequest.REPORT
        return message

    @staticmethod
    def run():
        message = ARINC717FrameRequest()
        message.requestType = ARINC717FrameRequest.RUN
        return message

    @staticmethod
    def stop():
        message = ARINC717FrameRequest()
        message.requestType = ARINC717FrameRequest.STOP
        return message

## ARINC717 Unit Test
class Test_ARINC717(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the ARINC717 test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        # Create a logger so we can add details to a multi-step test case
        cls.log = logger.Logger(name='Test ARINC 717')
        cls.log.info('++++ Setup before ARINC717 module unit tests ++++')
        # Create the module
        if cls.module is None:
            cls.module = arinc717.ARINC717()

    ## Test case: RUN request, REPORT request, STOP request, REPORT request, REPORT request
    # ARINC717 can run in different modes with different number of words per
    # frame, so we check that the number of words is one of the valid values.
    def test_all(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN Request, REPORT Request, STOP Request, REPORT Request, REPORT Request ****")
        log.info("==== RUN Request ====" )
        response = module.msgHandler(ThalesZMQMessage(ARINC717Messages.run()))
        self.assertEqual(response.name, "ARINC717FrameResponse")
        self.assertEqual(response.body.state, ARINC717FrameResponse.RUNNING)
        self.assertEqual(response.body.syncState, ARINC717FrameResponse.SYNCED)
        self.assertIn(len(response.body.arinc717frame) / 4, (32, 64, 128, 256, 512, 1024, 2048, 4096, 8192))

        response = module.msgHandler(ThalesZMQMessage(ARINC717Messages.report()))
        self.assertEqual(response.name, "ARINC717FrameResponse")
        self.assertEqual(response.body.state, ARINC717FrameResponse.RUNNING)
        self.assertEqual(response.body.syncState, ARINC717FrameResponse.SYNCED)
        self.assertIn(len(response.body.arinc717frame) / 4, (32, 64, 128, 256, 512, 1024, 2048, 4096, 8192))

        response = module.msgHandler(ThalesZMQMessage(ARINC717Messages.stop()))
        self.assertEqual(response.name, "ARINC717FrameResponse")
        self.assertEqual(response.body.state, ARINC717FrameResponse.STOPPED)
        self.assertEqual(response.body.syncState, ARINC717FrameResponse.SYNCED)
        self.assertIn(len(response.body.arinc717frame) / 4, (32, 64, 128, 256, 512, 1024, 2048, 4096, 8192))

        for i in range(1, 2):
            response = module.msgHandler(ThalesZMQMessage(ARINC717Messages.report()))
            self.assertEqual(response.name, "ARINC717FrameResponse")
            self.assertEqual(response.body.state, ARINC717FrameResponse.STOPPED)
            self.assertEqual(response.body.syncState, ARINC717FrameResponse.NO_SYNC)
            self.assertFalse(response.body.arinc717frame)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
