import unittest
from time import sleep

import encoder
from qual.pb2.Encoder_pb2 import EncoderRequest, EncoderResponse
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.logger import logger
from tklabs_utils.module.modulemsgs import ModuleMessages
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


# @cond doxygen_unittest

## Encoder Messages
class EncoderMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Encoder for IFE"

    @staticmethod
    def getMenuItems():
        return [("Report",  EncoderMessages.report),
                ("Run",     EncoderMessages.run),
                ("Stop",    EncoderMessages.stop)]

    @staticmethod
    def report():
        message = EncoderRequest()
        message.requestType = EncoderRequest.REPORT
        return message

    @staticmethod
    def run():
        message = EncoderRequest()
        message.requestType = EncoderRequest.RUN
        message.sink = '192.168.1.108:52123'
        return message

    @staticmethod
    def stop():
        message = EncoderRequest()
        message.requestType = EncoderRequest.STOP
        return message


## Encoder Unit Test
class Test_Encoder(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the Encoder test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        ConfigurableObject.setFilename("qual")
        #  Create a logger so we can add details to a multi-step test case
        cls.log = logger.Logger(name='Test Encoder')
        cls.log.info('++++ Setup before Encoder module unit tests ++++')
        #  Create the module
        if cls.module is None:
            cls.module = encoder.Encoder()

    ## Teardown when done with Encoder test cases
    #  This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after Encoder module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    #  This is run before each test case; we use it to make sure we
    #  start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(EncoderMessages.stop()))
        # Make sure the video is stopped
        sleep(2)

    ## Valid Test case: Send a RUN, REPORT, STOP, and REPORT msgs
    #  Asserts:
    #       appState == RUNNING
    #       ---------------------
    #       appState == RUNNING
    #       ---------------------
    #       appState == STOPPED
    #       ---------------------
    #       appState == STOPPED
    #       ---------------------
    def test_RunReportStop(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN, REPORT and STOP messages ****")

        response = module.msgHandler(ThalesZMQMessage(EncoderMessages.run()))
        self.assertEqual(response.name, "EncoderResponse")
        self.assertEqual(response.body.state, EncoderResponse.RUNNING)
        self.assertEqual(response.body.streamActive, True)

        log.info("==== Waiting 8 seconds for encoder to start ====")
        sleep(8)

        response = module.msgHandler(ThalesZMQMessage(EncoderMessages.report()))
        self.assertEqual(response.name, "EncoderResponse")
        self.assertEqual(response.body.state, EncoderResponse.RUNNING)
        self.assertEqual(response.body.streamActive, True)

        log.info("==== Video should now be playing ====")
        sleep(10)

        response = module.msgHandler(ThalesZMQMessage(EncoderMessages.stop()))
        self.assertEqual(response.name, "EncoderResponse")
        self.assertEqual(response.body.state, EncoderResponse.STOPPED)
        self.assertEqual(response.body.streamActive, False)

        log.info("==== Waiting 2 seconds for video to stop ====")
        sleep(2)

        response = module.msgHandler(ThalesZMQMessage(EncoderMessages.report()))
        self.assertEqual(response.name, "EncoderResponse")
        self.assertEqual(response.body.state, EncoderResponse.STOPPED)
        self.assertEqual(response.body.streamActive, False)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond