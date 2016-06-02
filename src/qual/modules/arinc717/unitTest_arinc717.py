import unittest
from time import sleep

import arinc717
from common.gpb.python import ARINC717Frame_pb2
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger

## ARINC717 Unit Test
#
class Test_Ethernet(unittest.TestCase):
    def test_basic(self):
        log = Logger(name='Test ARINC717')
        log.info('Running functionality test for ARINC717 module:')
        self.module = arinc717.ARINC717()

        message = ARINC717Frame_pb2.ARINC717FrameRequest()
        sleep(3)

        ## test REPORT
        log.info("REPORT current ARINC717 Frame information:")
        message.requestType = ARINC717Frame_pb2.ARINC717FrameRequest.REPORT
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        ## test additional REPORT
        log.info("REPORT current ARINC717 Frame information again:")
        message.requestType = ARINC717Frame_pb2.ARINC717FrameRequest.REPORT
        request = ThalesZMQMessage(message)
        self.module.msgHandler(request)
        sleep(3)

        pass

if __name__ == '__main__':
    unittest.main()