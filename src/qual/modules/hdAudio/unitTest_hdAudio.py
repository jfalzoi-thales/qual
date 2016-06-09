import unittest
from time import sleep

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
        return [('Disconnect', HDAudioMessages.disconnect),
                ('Connect Test 1', HDAudioMessages.connectTest1),
                ('Connect Test 2', HDAudioMessages.connectTest2),
                ("Report",  HDAudioMessages.report),]

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
    def test_basic(self):
        log = Logger(name='Test HD Audio')
        log.info('Running functionality test for HD Audio module:')
        self.module = HDAudio()

        log.info("==== Report before connecting ====")
        self.module.msgHandler(ThalesZMQMessage(HDAudioMessages.report()))
        sleep(1)

        log.info("==== Play one file ====")
        self.module.msgHandler(ThalesZMQMessage(HDAudioMessages.connectTest1()))
        sleep(1)

        log.info("==== Play a second file ====")
        self.module.msgHandler(ThalesZMQMessage(HDAudioMessages.connectTest2()))
        sleep(1)

        log.info("==== Stop playing ====")
        self.module.msgHandler(ThalesZMQMessage(HDAudioMessages.stop()))
        sleep(1)

        log.info("==== Paly again ====")
        self.module.msgHandler(ThalesZMQMessage(HDAudioMessages.connectTest1()))
        sleep(1)

        log.info("==== Stop playing ====")
        self.module.msgHandler(ThalesZMQMessage(HDAudioMessages.stop()))
        sleep(1)

        log.info("Terminating module...")
        self.module.terminate()

        pass
## @endcond