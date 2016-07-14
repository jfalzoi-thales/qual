import unittest

from time import sleep
from common.gpb.python.SSD_pb2 import SSDRequest, SSDResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages
from qual.modules.ssd.ssd import SSD

# @cond doxygen_unittest

## SSD Messages
class SSDMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "SSD"

    @staticmethod
    def getMenuItems():
        return [("Report",  SSDMessages.report),
                ("Run",     SSDMessages.run),
                ("Stop",    SSDMessages.stop)]

    @staticmethod
    def run():
        message = SSDRequest()
        message.requestType = SSDRequest.RUN
        return message

    @staticmethod
    def stop():
        message = SSDRequest()
        message.requestType = SSDRequest.STOP
        return message

    @staticmethod
    def report():
        message = SSDRequest()
        message.requestType = SSDRequest.REPORT
        return message


## SSD Unit Test
class Test_SSD(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the SSD test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test SSD')
        cls.log.info('++++ Setup before SSD module unit tests ++++')
        # Create the module
        cls.module = SSD()
        # Uncomment this if you don't want to see module debug messages
        # cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with SSD test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after SSD module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(SSDMessages.stop()))

    ## Valid Test case: Send a series of messages to confirm Start, Stop, and Report functionality
    # Asserts:
    #       appState == RUNNING
    #       --------------------
    #       appState == RUNNING
    #       readBandwidth > 0.0
    #       --------------------
    #       appState == STOPPED
    #       --------------------
    #       appState == STOPPED
    #       readBandwidth == 0.0
    #       --------------------
    #       appState == RUNNING
    #       readBandwidth == 0.0
    #       --------------------
    #       appState == RUNNING
    #       readBandwidth > 0.0
    #       --------------------
    #       appState == STOPPED
    #       --------------------
    #       appState == STOPPED
    #       readBandwidth == 0.0
    #       --------------------

    def test_RunReportStopReport(self):
        log = self.__class__.log
        module = self.__class__.module
        readBandTotal = 0

        log.info("**** Test case: Send a series of messages to confirm Start, Stop, and Report functionality ****")
        log.info("==== Run SSD module ====")
        response = module.msgHandler(ThalesZMQMessage(SSDMessages.run()))
        # Asserts
        self.assertEqual(response.name, "SSDResponse")
        self.assertEqual(response.body.state, SSDResponse.RUNNING)
        log.info("==== Sleeping for 40 seconds to allow 1GB file to be written ====")
        # Sleep to allow 1GB fio file to be written to drive on first run
        sleep(40)

        log.info("==== Have module Report to verify readBandwidth activity ====")
        # readBandwidth is 0.0 occasionally, so we collect a few times to make sure fio is active
        for x in xrange(3):
            response = module.msgHandler(ThalesZMQMessage(SSDMessages.report()))
            # Asserts
            self.assertEqual(response.name, "SSDResponse")
            self.assertEqual(response.body.state, SSDResponse.RUNNING)
            readBandTotal += response.body.readBandwidth
            sleep(1)

        self.assertGreater(readBandTotal, 0.0)

        log.info("==== Stop SSD module ====")
        response = module.msgHandler(ThalesZMQMessage(SSDMessages.stop()))
        # Asserts
        self.assertEqual(response.name, "SSDResponse")
        self.assertEqual(response.body.state, SSDResponse.STOPPED)
        log.info("==== Sleeping for 3 seconds to allow fio to stop ====")
        # Sleep to allow fio time to stop running
        sleep(3)

        log.info("==== Have module Report to verify readBandwidth is 0.0 ====")
        response = module.msgHandler(ThalesZMQMessage(SSDMessages.report()))
        # Asserts
        self.assertEqual(response.name, "SSDResponse")
        self.assertEqual(response.body.state, SSDResponse.STOPPED)
        self.assertEqual(response.body.readBandwidth, 0.0)

        log.info("==== Re-run SSD module ====")
        response = module.msgHandler(ThalesZMQMessage(SSDMessages.run()))
        # Asserts
        self.assertEqual(response.name, "SSDResponse")
        self.assertEqual(response.body.state, SSDResponse.RUNNING)
        self.assertEqual(response.body.readBandwidth, 0.0)
        log.info("==== Sleeping for 10 seconds to allow fio to start ====")
        # Sleep to allow fio time start running
        sleep(10)

        log.info("==== Have module Report to verify readBandwidth activity ====")
        # readBandwidth is 0.0 occasionally, so we collect a few times to make sure fio is active
        for x in xrange(3):
            response = module.msgHandler(ThalesZMQMessage(SSDMessages.report()))
            # Asserts
            self.assertEqual(response.name, "SSDResponse")
            self.assertEqual(response.body.state, SSDResponse.RUNNING)
            readBandTotal += response.body.readBandwidth
            sleep(1)

        self.assertGreater(readBandTotal, 0.0)

        log.info("==== Stop SSD module ====")
        response = module.msgHandler(ThalesZMQMessage(SSDMessages.stop()))
        # Asserts
        self.assertEqual(response.name, "SSDResponse")
        self.assertEqual(response.body.state, SSDResponse.STOPPED)
        log.info("==== Sleep for 3 seconds to allow fio to stop ====")
        # Sleep to allow fio time to stop running
        sleep(3)

        log.info("==== Stop SSD while already STOPPED ====")
        response = module.msgHandler(ThalesZMQMessage(SSDMessages.stop()))
        # Asserts
        self.assertEqual(response.name, "SSDResponse")
        self.assertEqual(response.body.state, SSDResponse.STOPPED)
        self.assertEqual(response.body.readBandwidth, 0.0)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
