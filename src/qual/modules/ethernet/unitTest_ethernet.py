import unittest
from time import sleep
import ethernet
from common.gpb.python.Ethernet_pb2 import EthernetRequest, EthernetResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger import logger
from common.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## Ethernet Messages
class EthernetMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Ethernet"

    @staticmethod
    def getMenuItems():
        return [("Report ENET_1",  EthernetMessages.report),
                ("Run ENET_1",     EthernetMessages.run),
                ("Stop ENET_1",    EthernetMessages.stop),
                ("Report ENET_8",  EthernetMessages.reportPort8),
                ("Run ENET_8",     EthernetMessages.runPort8),
                ("Stop ENET_8",    EthernetMessages.stopPort8)]

    @staticmethod
    def report():
        message = EthernetRequest()
        message.requestType = EthernetRequest.REPORT
        message.local = "ENET_1"
        return message

    @staticmethod
    def run():
        message = EthernetRequest()
        message.requestType = EthernetRequest.RUN
        message.local = "ENET_1"
        message.remote = "10.10.41.115"
        return message

    @staticmethod
    def runNoRemote():
        message = EthernetRequest()
        message.requestType = EthernetRequest.RUN
        message.local = "ENET_1"
        return message

    @staticmethod
    def stop():
        message = EthernetRequest()
        message.requestType = EthernetRequest.STOP
        message.local = "ENET_1"
        return message

    @staticmethod
    def reportPort2():
        message = EthernetRequest()
        message.requestType = EthernetRequest.REPORT
        message.local = "ENET_2"
        return message

    @staticmethod
    def runPort2():
        message = EthernetRequest()
        message.requestType = EthernetRequest.RUN
        message.local = "ENET_2"
        message.remote = "10.10.41.115"
        return message

    @staticmethod
    def stopPort2():
        message = EthernetRequest()
        message.requestType = EthernetRequest.STOP
        message.local = "ENET_2"
        return message

    @staticmethod
    def reportPort8():
        message = EthernetRequest()
        message.requestType = EthernetRequest.REPORT
        message.local = "ENET_8"
        return message

    @staticmethod
    def runPort8():
        message = EthernetRequest()
        message.requestType = EthernetRequest.RUN
        message.local = "ENET_8"
        message.remote = "10.10.42.21"
        return message

    @staticmethod
    def stopPort8():
        message = EthernetRequest()
        message.requestType = EthernetRequest.STOP
        message.local = "ENET_8"
        return message


## Ethernet Unit Test
class Test_Ethernet(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the Ethernet test cases
    # This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        # Create a logger so we can add details to a multi-step test case
        cls.log = logger.Logger(name='Test Ethernet')
        cls.log.info('++++ Setup before Ethernet module unit tests ++++')
        # Create the module
        cls.module = ethernet.Ethernet()
        # Uncomment this if you don't want to see module debug messages
        #cls.module.log.setLevel(logger.INFO)

    ## Teardown when done with Ethernet test cases
    # This is run only once when we're done with all test cases
    @classmethod
    def tearDownClass(cls):
        cls.log.info("++++ Teardown after Ethernet module unit tests ++++")
        cls.module.terminate()

    ## Test setup
    # This is run before each test case; we use it to make sure we
    # start each test case with the module in a known state
    def setUp(self):
        log = self.__class__.log
        module = self.__class__.module
        log.info("==== Reset module state ====")
        module.msgHandler(ThalesZMQMessage(EthernetMessages.stop()))

    ## Valid Test case: Send a RUN msg
    # Asserts:
    #       appState == RUNNING
    #       local == "ENET_1"
    #       bandwidth == 0
    def test_Run(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN message ****")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.run()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertEqual(response.body.bandwidth, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a REPORT msg
    # Asserts:
    #       appState == STOPPED
    #       local == "ENET_1"
    #       bandwidth == 0
    def test_Report(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: REPORT message ****")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.STOPPED)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertEqual(response.body.bandwidth, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a STOP msg
    # Asserts:
    #       appState == STOPPED
    #       local == "ENET_1"
    #       bandwidth == 0
    def test_Stop(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: STOP message ****")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.stop()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.STOPPED)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertEqual(response.body.bandwidth, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RUN, REPORT and STOP msgs
    # Asserts:
    #       appState == RUNNING
    #       local == "ENET_1"
    #       bandwidth == 0
    #       ---------------------
    #       appState == RUNNING
    #       local  == "ENET_1"
    #       bandwidth > 0
    #       ---------------------
    #       appState == STOPPED
    #       local == "ENET_1"
    #       bandwidth > 0
    #       ---------------------
    def test_RunReportStop(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN, REPORT and STOP messages ****")

        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.run()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertEqual(response.body.bandwidth, 0)

        log.info("==== Wait 2 seconds to accumulate statistics ====")
        sleep(2)

        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertGreater(response.body.bandwidth, 0)

        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.stop()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.STOPPED)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertGreater(response.body.bandwidth, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Multiple ports
    # Asserts:
    def test_RunMultiple(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN, REPORT and STOP on multiple ports ****")

        log.info("==== RUN port ENET_1 ====")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.run()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertEqual(response.body.bandwidth, 0)

        log.info("==== RUN port ENET_2 ====")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.runPort2()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_2")
        self.assertEqual(response.body.bandwidth, 0)

        log.info("==== Wait 4 seconds to accumulate statistics ====")
        sleep(4)

        log.info("==== REPORT port ENET_1 ====")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertGreater(response.body.bandwidth, 0)

        log.info("==== REPORT port ENET_2 ====")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.reportPort2()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_2")
        self.assertGreater(response.body.bandwidth, 0)

        log.info("==== Stop port ENET_1 ====")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.stop()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.STOPPED)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertGreater(response.body.bandwidth, 0)

        log.info("==== REPORT port ENET_1 ====")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.STOPPED)
        self.assertEqual(response.body.local, "ENET_1")

        log.info("==== REPORT port ENET_2 ====")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.reportPort2()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_2")

        log.info("==== Stop port ENET_2 ====")
        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.stopPort2()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.STOPPED)
        self.assertEqual(response.body.local, "ENET_2")
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RUN, RUN and REPORT msgs
    # Asserts:
    #       appState == RUNNING
    #       local == "ENET_1"
    #       bandwidth == 0
    #       ---------------------
    #       appState == RUNNING
    #       local == "ENET_1"
    #       bandwidth == 0
    #       ---------------------
    #       appState == RUNNING
    #       local > 0
    #       bandwidth > 0
    def test_RunRunReport(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN, RUN and REPORT messages ****")

        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.run()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertEqual(response.body.bandwidth, 0)

        log.info("==== Wait 2 seconds to accumulate statistics ====")
        sleep(2)

        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.run()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertEqual(response.body.bandwidth, 0)

        log.info("==== Wait 2 seconds to accumulate statistics ====")
        sleep(2)

        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertGreater(response.body.bandwidth, 0)
        log.info("==== Test complete ====")

    ## Valid Test case: Send a RUN, followed by RUN with no remote specified
    # Asserts:
    #       appState == RUNNING
    #       local == "ENET_1"
    #       bandwidth == 0
    #       ---------------------
    #       appState == RUNNING
    #       local  == "ENET_1"
    #       bandwidth > 0
    #       ---------------------
    def test_RunRunNoRemote(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Test case: RUN, RUN (no remote) ****")

        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.run()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertEqual(response.body.bandwidth, 0)

        log.info("==== Wait 2 seconds to accumulate statistics ====")
        sleep(2)

        response = module.msgHandler(ThalesZMQMessage(EthernetMessages.runNoRemote()))
        self.assertEqual(response.name, "EthernetResponse")
        self.assertEqual(response.body.state, EthernetResponse.RUNNING)
        self.assertEqual(response.body.local, "ENET_1")
        self.assertEqual(response.body.bandwidth, 0)
        log.info("==== Test complete ====")


if __name__ == '__main__':
    unittest.main()

## @endcond
