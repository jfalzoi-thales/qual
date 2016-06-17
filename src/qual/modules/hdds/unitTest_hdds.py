import unittest
from time import sleep
import hdds
from common.gpb.python.HDDS_pb2 import GetReq, SetReq
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

#  @cond doxygen_unittest

## HDDS Messages
class HDDSMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "HDDS"

    @staticmethod
    def getMenuItems():
        return [("Get single value",     HDDSMessages.getSingle),
                ("Get multiple values",  HDDSMessages.getMultiple),
                ("Set single value",     HDDSMessages.setSingle)]

    @staticmethod
    def getSingle():
        message = GetReq()
        message.key.append("external_pins.output.pin_a6")
        return message

    @staticmethod
    def getMultiple():
        message = GetReq()
        message.key.append("external_pins.output.pin_a6")
        message.key.append("external_pins.output.pin_b6")
        message.key.append("external_pins.output.pin_c6")
        return message

    @staticmethod
    def setSingle():
        message = SetReq()
        prop = message.values.add()
        prop.key = "external_pins.output.pin_a6"
        prop.value = "HIGH"
        return message

    @staticmethod
    def getBogus():
        message = GetReq()
        message.key.append("bogus_key")
        return message

    @staticmethod
    def setBogus():
        message = SetReq()
        prop = message.values.add()
        prop.key = "bogus_key"
        prop.value = "x"
        return message


## HDDS Unit Test
class Test_HDDS(unittest.TestCase):
    def test_basic(self):
        log = Logger(name='Test HDDS')
        log.info('Running functionality test for HDDS module:')
        self.module = hdds.HDDS()

        log.info("Get single value:")
        self.module.msgHandler(ThalesZMQMessage(HDDSMessages.getSingle()))
        sleep(1)

        log.info("Get multiple values:")
        self.module.msgHandler(ThalesZMQMessage(HDDSMessages.getMultiple()))
        sleep(1)

        log.info("Set value:")
        self.module.msgHandler(ThalesZMQMessage(HDDSMessages.setSingle()))
        sleep(1)

        log.info("Read back after set:")
        self.module.msgHandler(ThalesZMQMessage(HDDSMessages.getSingle()))
        sleep(1)

        log.info("Try to get bogus key:")
        self.module.msgHandler(ThalesZMQMessage(HDDSMessages.getBogus()))
        sleep(1)

        log.info("Try to set bogus key:")
        self.module.msgHandler(ThalesZMQMessage(HDDSMessages.setBogus()))

        pass

if __name__ == '__main__':
    unittest.main()

## @endcond