
## Ethernet Unit Test
import unittest

from common.logger import logger
from videoEncoder import VideoEncoder


class Test_VideoEncoder(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the Ethernet test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = logger.Logger(name='Test Video Encoder Settings')
        cls.log.info('++++ Setup before Video Encoder unit tests ++++')

    ## Teardown when done with Ethernet test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after Video Encoder unit tests ++++")

    ## Valid Test case: Send a RUN msg
    def test_setINI(self):
        log = self.__class__.log

        log.info("**** Test case: INI Config message ****")
        videoEncoder = VideoEncoder(self._testMethodName)
        self.assertEquals(videoEncoder.broadcastIP, 'TestIp', 'INI IP Address')
        self.assertEquals(videoEncoder.broadcastPort, 'TestPort', 'INI IP Address')
        log.info("==== Test complete ====")


    def test_payload(self):
        log = self.__class__.log

        log.info("**** Test case: Test Payload ****")
        videoEncoder = VideoEncoder(self._testMethodName)
        postData = videoEncoder.formatPostData()
        self.assertIn('ip=10.10.10.10', postData, 'Verify IP in Post Data')
        self.assertIn('port=1001', postData, 'Verify Port in post Data')

        videoEncoder.broadcastIP = '11.11.11.11'
        videoEncoder.broadcastPort = '1002'
        postData = videoEncoder.formatPostData()
        self.assertIn('ip=11.11.11.11', postData, 'Verify Changed IP in Post Data')
        self.assertIn('port=1002', postData, 'Verify Changed Port in post Data')

        log.info("==== Test complete ====")

    def test_Set(self):
        log = self.__class__.log

        log.info("**** Test case: Test Payload ****")
        videoEncoder = VideoEncoder(self._testMethodName)
        status, response = videoEncoder.sendConfig()
        log.info("Status %d" % (status,))
        log.info("Response %s" % (response,))

        log.info("==== Test complete ====")