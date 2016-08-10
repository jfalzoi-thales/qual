import unittest
from time import sleep
import encoder
from common.gpb.python.Encoder_pb2 import EncoderRequest, EncoderResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger import logger
from common.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## Encoder Messages
class EncoderMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Encoder"

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
        message.sink = '10.10.10.10:8000'
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
        #  Create a logger so we can add details to a multi-step test case
        cls.log = logger.Logger(name='Test Encoder')
        cls.log.info('++++ Setup before Encoder module unit tests ++++')
        #  Create the module
        cls.module = encoder.Encoder(deserialize=True)
        #  Uncomment this if you don't want to see module debug messages
        #cls.module.log.setLevel(logger.INFO)

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
        self.assertEqual(response.body.inputActive, True)
        self.assertEqual(response.body.streamActive, True)

        log.info("==== Wait 2 seconds ====")
        sleep(2)

        response = module.msgHandler(ThalesZMQMessage(EncoderMessages.report()))
        self.assertEqual(response.name, "EncoderResponse")
        self.assertEqual(response.body.state, EncoderResponse.RUNNING)
        self.assertEqual(response.body.inputActive, True)
        self.assertEqual(response.body.streamActive, True)

        response = module.msgHandler(ThalesZMQMessage(EncoderMessages.stop()))
        self.assertEqual(response.name, "EncoderResponse")
        self.assertEqual(response.body.state, EncoderResponse.STOPPED)
        self.assertEqual(response.body.inputActive, False)
        self.assertEqual(response.body.streamActive, False)

        response = module.msgHandler(ThalesZMQMessage(EncoderMessages.report()))
        self.assertEqual(response.name, "EncoderResponse")
        self.assertEqual(response.body.state, EncoderResponse.STOPPED)
        self.assertEqual(response.body.inputActive, False)
        self.assertEqual(response.body.streamActive, False)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond