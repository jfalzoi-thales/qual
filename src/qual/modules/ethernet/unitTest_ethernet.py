import unittest
from time import sleep
import ethernet
from common.gpb.python.Ethernet_pb2 import EthernetRequest
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

# @cond doxygen_unittest

## Ethernet Messages
class EthernetMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "Ethernet"

    @staticmethod
    def getMenuItems():
        return [("Report",  EthernetMessages.report),
                ("Run",     EthernetMessages.run),
                ("Stop",    EthernetMessages.stop)]

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
        message.remote = "10.10.42.228"
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


## Ethernet Unit Test
class Test_Ethernet(unittest.TestCase):
    ## Basic functionality test for Ethernet module
    #  @param     self
    def test_basic(self):
        log = Logger(name='Ethernet Module Test')
        self.module = ethernet.Ethernet()

        log.info("REPORT before iperf3:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        sleep(3)

        log.info("RUN iperf3:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.run()))
        sleep(3)

        log.info("REPORT after iperf3:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        sleep(3)

        log.info("RUN while RUNNING:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.run()))
        sleep(3)

        log.info("REPORT after re-running iperf3:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        sleep(3)

        log.info("STOP iperf3:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.stop()))
        sleep(3)

        log.info("REPORT after stopping iperf3:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        sleep(3)

        log.info("STOP while not RUNNING:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.stop()))
        sleep(3)

        log.info("REPORT after stopping while not running:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        sleep(3)

        log.info("RUN iperf3:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.run()))
        sleep(3)

        log.info("REPORT after iperf3:")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.report()))
        sleep(3)

        log.info("RUN iperf3 when server is empty")
        self.module.msgHandler(ThalesZMQMessage(EthernetMessages.runNoRemote()))
        sleep(3)

        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond
