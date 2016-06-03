import unittest
from time import sleep
import ethernet
from common.gpb.python import Ethernet_pb2
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger

# @cond doxygen_unittest

## Ethernet Unit Test
class Test_Ethernet(unittest.TestCase):
    ## Basic functionality test for Ethernet module
    #  @param     self
    def test_basic(self):
        log = Logger(name='Ethernet Module Test')
        self.module = ethernet.Ethernet()
        message = Ethernet_pb2.EthernetRequest()

        #  test REPORT before iperf3 is running
        log.info("REPORT before iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_1"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test RUN for iperf3
        log.info("RUN iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.RUN
        message.local = "ENET_2"
        message.remote = "10.10.42.228"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test REPORT after iperf3 is running
        log.info("REPORT after iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_3"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test RUN while iperf3 is running
        log.info("RUN while RUNNING:")
        message.requestType = Ethernet_pb2.EthernetRequest.RUN
        message.local = "ENET_4"
        message.remote = "10.10.42.228"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test REPORT after re-running iperf3
        log.info("REPORT after re-running iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_5"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test STOP after running iperf3
        log.info("STOP iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.STOP
        message.local = "ENET_6"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test REPORT after stopping iperf3
        log.info("REPORT after stopping iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_7"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test STOP while iperf3 is not running
        log.info("STOP while not RUNNING:")
        message.requestType = Ethernet_pb2.EthernetRequest.STOP
        message.local = "ENET_8"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test REPORT after double STOP messages
        log.info("REPORT after stopping while not running:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_9"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test re-RUN after STOP
        log.info("RUN iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.RUN
        message.local = "ENET_10"
        message.remote = "10.10.42.228"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test REPORT after iperf3 is is re-RUN
        log.info("REPORT after iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_11"
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        #  test RUN when remote is None
        log.info("RUN iperf3 when server is empty")
        message.requestType = Ethernet_pb2.EthernetRequest.RUN
        message.local = "ENET_12"
        message.remote = ""
        self.module.msgHandler(ThalesZMQMessage(message))
        sleep(3)

        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond