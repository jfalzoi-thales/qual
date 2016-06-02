import unittest
from time import sleep

import ethernet
from common.gpb.python import Ethernet_pb2
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger

# @cond doxygen_unittest

## Ethernet Unit Test
#
class Test_Ethernet(unittest.TestCase):
    def test_basic(self):
        log = Logger(name='Test Ethernet')
        log.info('Running functionality test for Ethernet module:')
        self.module = ethernet.Ethernet()

        message = Ethernet_pb2.EthernetRequest()
        sleep(3)

        ## test REPORT before iperf3 is running
        log.info("REPORT before iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_1"
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        ## test RUN for iperf3
        log.info("RUN iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.RUN
        message.local = "ENET_2"
        message.remote = "10.10.42.228"
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        ## test REPORT after iperf3 is running
        log.info("REPORT after iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_3"
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        ## test RUN while iperf3 is running
        log.info("RUN while RUNNING:")
        message.requestType = Ethernet_pb2.EthernetRequest.RUN
        message.local = "ENET_4"
        message.remote = "10.10.42.228"
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        ## test REPORT after re-running iperf3
        log.info("REPORT after re-running iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_5"
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        ## test STOP after running iperf3
        log.info("STOP iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.STOP
        message.local = "ENET_6"
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        ## test REPORT after stopping iperf3
        log.info("REPORT after stopping iperf3:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_7"
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        ## test STOP while iperf3 is not running
        log.info("STOP while not RUNNING:")
        message.requestType = Ethernet_pb2.EthernetRequest.STOP
        message.local = "ENET_8"
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        ## test REPORT after double STOP messages
        log.info("REPORT after stopping while not running:")
        message.requestType = Ethernet_pb2.EthernetRequest.REPORT
        message.local = "ENET_9"
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        self.module.terminate()

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond
