import unittest
import time

from common.gpb.python.HDAudio_pb2 import HDAudioRequest, HDAudioResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages
from qual.modules.hdAudio.hdAudio import HDAudio

# @cond doxygen_unittest

## HD Audio Messages
class HDAudioMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "HD Audio"

    @staticmethod
    def getMenuItems():
        return [("Report",  HDAudioMessages.report),
                ('Connect Test 1', HDAudioMessages.connectTest1),
                ('Connect Test 2', HDAudioMessages.connectTest2),
                ('Connect Test 3 (1kHz 60sec)', HDAudioMessages.connectTest3),
                ('Connect Test 4 (4kHz 60sec)', HDAudioMessages.connectTest4),
                ('Disconnect', HDAudioMessages.disconnect)]

    @staticmethod
    def connectTest1():
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.CONNECT
        message.source='braindamage.wav'
        message.volume=100
        return message

    @staticmethod
    def connectTest2():
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.CONNECT
        message.source='comfortablynumb.wav'
        message.volume=50
        return message

    @staticmethod
    def connectTest3():
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.CONNECT
        message.source = '1kHz_60sec.wav'
        message.volume = 100
        return message

    @staticmethod
    def connectTest4():
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.CONNECT
        message.source = '4kHz_60sec.wav'
        message.volume = 100
        return message

    @staticmethod
    def report():
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.REPORT
        return message

    @staticmethod
    def disconnect():
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.DISCONNECT
        return message

## HD Audio Unit Test
class Test_HDAudio(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the HDAudio test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test HD Audio')
        cls.log.info('++++ Setup before HD Audio module unit tests ++++')
        # Create the module
        cls.module = HDAudio()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with HDAudio test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after HD Audio module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(HDAudioMessages.disconnect()))

    ## Valid Test case: Send a REPORT msg
    # Asserts:
    #       appState == STOPPED
    #       source == ""
    #       volume == 100
    #       ---------------------
    def test_Report(self):
        log = self.__class__.log
        module = self.__class__.module

        # Create message
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.REPORT

        log.info("**** Test case: REPORT message ****")

        response = module.msgHandler(ThalesZMQMessage(message))
        # asserts
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.DISCONNECTED)
        self.assertEqual(response.body.source, '')

    ## Valid Test case: Send a CONNECT, REPORT and DISCONNECT msgs
    # Asserts:
    #       appState == CONNECTED
    #       source == "braindamage.wav"
    #       volume == 100
    #       ---------------------
    #       appState == CONNECTED
    #       source == "braindamage.wav"
    #       volume == 100
    #       ---------------------
    #       appState == DISCONNECTED
    #       source == "braindamage.wav"
    #       volume == 100
    #       ---------------------
    def test_ConnectReportDisconnect_Vol100(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: CONNECT, REPORT and DISCONNECT message ****")
        # Connect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.connectTest1()))
        # asserts
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.source, 'braindamage.wav')
        self.assertEqual(response.body.volume, 100)
        # Report
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.report()))
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.source, 'braindamage.wav')
        self.assertEqual(response.body.volume, 100)
        # Allow the audio for a while
        time.sleep(5)
        # Disconnect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.disconnect()))
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.DISCONNECTED)
        self.assertEqual(response.body.source, '')
        self.assertEqual(response.body.volume, 100)

    ## Valid Test case: Send a CONNECT, REPORT and DISCONNECT msgs
    # Asserts:
    #       appState == CONNECTED
    #       source == "comfortablynumb.wav"
    #       volume == 50
    #       ---------------------
    #       appState == CONNECTED
    #       source == "comfortablynumb.wav"
    #       volume == 50
    #       ---------------------
    #       appState == DISCONNECTED
    #       source == "comfortablynumb.wav"
    #       volume == 50
    #       ---------------------
    def test_ConnectReportDisconnect_Vol50(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: CONNECT, REPORT and DISCONNECT message ****")
        # Connect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.connectTest2()))
        # asserts
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.source, 'comfortablynumb.wav')
        self.assertEqual(response.body.volume, 50)
        # Report
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.report()))
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.source, 'comfortablynumb.wav')
        self.assertEqual(response.body.volume, 50)
        # Allow the audio for a while
        time.sleep(5)
        # Disconnect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.disconnect()))
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.DISCONNECTED)
        self.assertEqual(response.body.source, '')
        self.assertEqual(response.body.volume, 50)

    ## Valid Test case: Send a CONNECT, DISCONNECT, CONNECT and DISCONNECT msgs
    # Asserts:
    #       appState == CONNECTED
    #       source == "braindamage.wav"
    #       volume == 100
    #       ---------------------
    #       appState == DISCONNECTED
    #       source == "braindamage.wav"
    #       volume == 100
    #       ---------------------
    #       appState == CONNECTED
    #       source == "comfortablynumb.wav"
    #       volume == 50
    #       ---------------------
    #       appState == DISCONNECTED
    #       source == "comfortablynumb.wav"
    #       volume == 50
    #       ---------------------
    def test_ConnectReportDisconnect_Vol50(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: CONNECT, DISCONNECT, CONNECT and DISCONNECT message ****")

        # Connect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.connectTest1()))
        # asserts
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.source, 'braindamage.wav')
        self.assertEqual(response.body.volume, 100)
        # Allow the audio for a while
        time.sleep(5)
        # Disconnect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.disconnect()))
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.DISCONNECTED)
        self.assertEqual(response.body.source, '')
        self.assertEqual(response.body.volume, 100)
        # Connect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.connectTest2()))
        # asserts
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.source, 'comfortablynumb.wav')
        self.assertEqual(response.body.volume, 50)
        # Allow the audio for a while
        time.sleep(5)
        # Disconnect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.disconnect()))
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.DISCONNECTED)
        self.assertEqual(response.body.source, '')
        self.assertEqual(response.body.volume, 50)

    ## Valid Test case: Send a CONNECT, REPORT and DISCONNECT msgs
    # Asserts:
    #       appState == CONNECTED
    #       source == "1kHz_60sec.wav"
    #       volume == 100
    #       ---------------------
    #       appState == CONNECTED
    #       source == "1kHz_60sec.wav"
    #       volume == 100
    #       ---------------------
    #       appState == DISCONNECTED
    #       source == "1kHz_60sec.wav"
    #       volume == 100
    #       ---------------------
    def test_ConnectReportDisconnect_Vol100_1kHz(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: 1kHz file, CONNECT, REPORT and DISCONNECT message ****")
        # Connect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.connectTest3()))
        # asserts
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.source, '1kHz_60sec.wav')
        self.assertEqual(response.body.volume, 100)
        # Report
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.report()))
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.source, '1kHz_60sec.wav')
        self.assertEqual(response.body.volume, 100)
        # Allow the audio for a while
        time.sleep(5)
        # Disconnect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.disconnect()))
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.DISCONNECTED)
        self.assertEqual(response.body.source, '')
        self.assertEqual(response.body.volume, 100)


    ## Valid Test case: Send a CONNECT, REPORT and DISCONNECT msgs
    # Asserts:
    #       appState == CONNECTED
    #       source == "4kHz_60sec.wav"
    #       volume == 100
    #       ---------------------
    #       appState == CONNECTED
    #       source == "4kHz_60sec.wav"
    #       volume == 100
    #       ---------------------
    #       appState == DISCONNECTED
    #       source == "4kHz_60sec.wav"
    #       volume == 100
    #       ---------------------
    def test_ConnectReportDisconnect_Vol100_4kHz(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: 4kHz file, CONNECT, REPORT and DISCONNECT message ****")
        # Connect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.connectTest4()))
        # asserts
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.source, '4kHz_60sec.wav')
        self.assertEqual(response.body.volume, 100)
        # Report
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.report()))
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.source, '4kHz_60sec.wav')
        self.assertEqual(response.body.volume, 100)
        # Allow the audio for a while
        time.sleep(5)
        # Disconnect
        response = module.msgHandler(ThalesZMQMessage(HDAudioMessages.disconnect()))
        self.assertEqual(response.name, "HDAudioResponse")
        self.assertEqual(response.body.appState, HDAudioResponse.DISCONNECTED)
        self.assertEqual(response.body.source, '')
        self.assertEqual(response.body.volume, 100)

    ## Invalid Test case: Send a wrong volume
    # Asserts:
    #       --------------------
    def test_WrongVolume(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Wrong Volume ****")
        # Message
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.CONNECT
        message.source = 'braindamage.wav'
        message.volume = 120

        # Connect
        response = module.msgHandler(ThalesZMQMessage(message))
        self.assertEqual(response.body.appState, HDAudioResponse.CONNECTED)
        self.assertEqual(response.body.volume, 100)

    ## Invalid Test case: Send a source path
    # Asserts:
    #       --------------------
    def test_WrongPath(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: Wrong source path ****")
        # Message
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.CONNECT
        message.source = 'anotherbrickinthewall.wav'
        message.volume = 100

        # Connect
        response = module.msgHandler(ThalesZMQMessage(message))
        self.assertEqual(response.body.appState, HDAudioResponse.DISCONNECTED)

if __name__ == '__main__':
    unittest.main()

## @endcond
