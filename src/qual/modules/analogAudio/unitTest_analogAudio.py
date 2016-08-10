import unittest
import analogAudio
from common.gpb.python.AnalogAudio_pb2 import AnalogAudioRequest, AnalogAudioResponse
from common.tzmq.ThalesZMQMessage import ThalesZMQMessage
from common.logger.logger import Logger
from common.module.modulemsgs import ModuleMessages

#  @cond doxygen_unittest

## AudioAnalog Messages
class AnalogAudioMessages(ModuleMessages):
    @staticmethod
    def getMenuTitle():
        return "AnalogAudio for IFE"

    @staticmethod
    def getMenuItems():
        return [("Report on sink 1",                    AnalogAudioMessages.reportOut1),
                ("Report on sink 2",                    AnalogAudioMessages.reportOut2),
                ("Report on all sinks",                 AnalogAudioMessages.reportAll),
                ("Connect sink 1 to source 1",          AnalogAudioMessages.connectOut1In1),
                ("Connect sink 2 to source 1",          AnalogAudioMessages.connectOut2In1),
                ("Connect sink 1 to source 2",          AnalogAudioMessages.connectOut1In2),
                ("Connect all sinks to source 1",       AnalogAudioMessages.connectAll),
                ("Connect bogus sink to source 1",      AnalogAudioMessages.connectOutBogusIn1),
                ("Connect sink 1 to bogus source",      AnalogAudioMessages.connectOut1InBogus),
                ("Disconnect sink 1 from source",       AnalogAudioMessages.disconnectOut1),
                ("Disconnect sink 2 from source",       AnalogAudioMessages.disconnectOut2),
                ("Disconnect all sinks from source",    AnalogAudioMessages.disconnectAll)]

    @staticmethod
    def reportOut1():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.REPORT
        message.sink = "VA_AUDOUT_1"
        return message

    @staticmethod
    def reportOut2():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.REPORT
        message.sink = "VA_AUDOUT_2"
        return message

    @staticmethod
    def reportAll():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.REPORT
        message.sink = "ALL"
        return message

    @staticmethod
    def connectOut1In1():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.CONNECT
        message.sink = "VA_AUDOUT_1"
        message.source = "PA_70V_AUDIN_1"
        return message

    @staticmethod
    def connectOut2In1():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.CONNECT
        message.sink = "VA_AUDOUT_2"
        message.source = "PA_70V_AUDIN_1"
        return message

    @staticmethod
    def connectOut1In2():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.CONNECT
        message.sink = "VA_AUDOUT_1"
        message.source = "PA_AUDIN_2"
        return message

    @staticmethod
    def connectAll():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.CONNECT
        message.sink = "ALL"
        message.source = "PA_70V_AUDIN_1"
        return message

    @staticmethod
    def connectOutBogusIn1():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.CONNECT
        message.sink = "VA_AUDOUT_BOGUS"
        message.source = "PA_70V_AUDIN_1"
        return message

    @staticmethod
    def connectOut1InBogus():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.CONNECT
        message.sink = "VA_AUDOUT_1"
        message.source = "PA_70V_AUDIN_BOGUS"
        return message

    @staticmethod
    def disconnectOut1():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.DISCONNECT
        message.sink = "VA_AUDOUT_1"
        return message

    @staticmethod
    def disconnectOut2():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.DISCONNECT
        message.sink = "VA_AUDOUT_2"
        return message

    @staticmethod
    def disconnectAll():
        message = AnalogAudioRequest()
        message.requestType = AnalogAudioRequest.DISCONNECT
        message.sink = "ALL"
        return message


## AnalogAudio for IFE Unit Test
class Test_AnalogAudio(unittest.TestCase):
    ## Static logger instance
    log = None

    ## Static module instance
    module = None

    ## Setup for the AnalogAudio test cases
    #  This is run only once before running any test cases
    @classmethod
    def setUpClass(cls):
        #  Create a logger so we can add details to a multi-step test case
        cls.log = Logger(name='Test AudioAnalog-IFE')
        cls.log.info('++++ Setup before AnalogAudio-IFE module unit tests ++++')
        #  Create the module
        cls.module = analogAudio.AnalogAudio(deserialize=True)
        #  Uncomment this if you want to see module debug messages
        #cls.module.log.setLevel("DEBUG")

    ## Valid Test Case: Connect Out 1 and In 1, Report on Out 1 after Connect,
    #                   Disconnect Out 1, Report on Out 1 after Disconnect
    #  Asserts:
    #       sink    == "VA_AUDOUT_1"
    #       source  == "PA_70V_AUDIN_1"
    #       state   == CONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_1"
    #       source  == "PA_70V_AUDIN_1"
    #       state   == CONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_1"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_1"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    def test_basic(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Valid Test Case: Connect Out 1 and In 1 ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.connectOut1In1()))



        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "PA_70V_AUDIN_1")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.CONNECTED)

        log.info("**** Valid Test Case: Report on Out 1 after Connect ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.reportOut1()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "PA_70V_AUDIN_1")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.CONNECTED)

        log.info("**** Valid Test Case: Disconnect Out 1 ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.disconnectOut1()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.DISCONNECTED)

        log.info("**** Valid Test Case: Report on Out 1 after Disconnect ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.reportOut1()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.DISCONNECTED)

        log.info("==== Test complete ====")

    ## Valid Test Case: Connect Out 1 and In 1, Connect Out 2 and In 1, Report all after Connect,
    #                   Connect In 1 and Out 2, Report all after Reconnect, Disconnect Out 1, Disconnect Out 2,
    #                   Report all after Disconnect
    #  Asserts:
    #       sink    == "VA_AUDOUT_1"
    #       source  == "PA_70V_AUDIN_1"
    #       state   == CONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_2"
    #       source  == "PA_70V_AUDIN_1"
    #       state   == CONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_1"
    #       source  == "PA_70V_AUDIN_1"
    #       state   == CONNECTED
    #       sink    == "VA_AUDOUT_2"
    #       source  == "PA_70V_AUDIN_1"
    #       state   == CONNECTED
    #       sink    == "VA_AUDOUT_6"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_1"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_1"
    #       source  == "PA_AUDIN_2"
    #       state   == CONNECTED
    #       sink    == "VA_AUDOUT_2"
    #       source  == "PA_70V_AUDIN_1"
    #       state   == CONNECTED
    #       sink    == "VA_AUDOUT_6"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_1"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_2"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_1"
    #       source  == ""
    #       state   == DISCONNECTED
    #       sink    == "VA_AUDOUT_2"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    def test_multi(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Valid Test Case: Connect Out 1 and In 1 ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.connectOut1In1()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "PA_70V_AUDIN_1")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.CONNECTED)

        log.info("**** Valid Test Case: Connect Out 2 and In 1 ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.connectOut2In1()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_2")
        self.assertEqual(response.body.loopback[0].source, "PA_70V_AUDIN_1")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.CONNECTED)

        log.info("**** Valid Test Case: Report all after Connect ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.reportAll()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "PA_70V_AUDIN_1")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.CONNECTED)
        self.assertEqual(response.body.loopback[1].sink, "VA_AUDOUT_2")
        self.assertEqual(response.body.loopback[1].source, "PA_70V_AUDIN_1")
        self.assertEqual(response.body.loopback[1].state, AnalogAudioResponse.CONNECTED)
        self.assertEqual(response.body.loopback[5].sink, "VA_AUDOUT_6")
        self.assertEqual(response.body.loopback[5].source, "")
        self.assertEqual(response.body.loopback[5].state, AnalogAudioResponse.DISCONNECTED)

        log.info("**** Valid Test Case: Connect Out 1 and In 2 ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.connectOut1In2()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "PA_AUDIN_2")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.CONNECTED)

        log.info("**** Valid Test Case: Report all after Reconnect ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.reportAll()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "PA_AUDIN_2")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.CONNECTED)
        self.assertEqual(response.body.loopback[1].sink, "VA_AUDOUT_2")
        self.assertEqual(response.body.loopback[1].source, "PA_70V_AUDIN_1")
        self.assertEqual(response.body.loopback[1].state, AnalogAudioResponse.CONNECTED)
        self.assertEqual(response.body.loopback[5].sink, "VA_AUDOUT_6")
        self.assertEqual(response.body.loopback[5].source, "")
        self.assertEqual(response.body.loopback[5].state, AnalogAudioResponse.DISCONNECTED)

        log.info("**** Valid Test Case: Disconnect Out 1 ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.disconnectOut1()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.DISCONNECTED)

        log.info("**** Valid Test Case: Disconnect Out 2 ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.disconnectOut2()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_2")
        self.assertEqual(response.body.loopback[0].source, "")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.DISCONNECTED)

        log.info("**** Valid Test Case: Report all after Disconnect ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.reportAll()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.DISCONNECTED)
        self.assertEqual(response.body.loopback[1].sink, "VA_AUDOUT_2")
        self.assertEqual(response.body.loopback[1].source, "")
        self.assertEqual(response.body.loopback[1].state, AnalogAudioResponse.DISCONNECTED)

        log.info("==== Test complete ====")

    ## Valid Test Case: Connect bogus In to Out 1, Connect In 1 to bogus Out
    #  Asserts:
    #       sink    == "VA_AUDOUT_BOGUS"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_1"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    def test_bogus(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Valid Test Case: Connect bogus In to Out 1 ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.connectOutBogusIn1()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_BOGUS")
        self.assertEqual(response.body.loopback[0].source, "")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.DISCONNECTED)

        log.info("**** Valid Test Case: Connect In 1 to bogus Out ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.connectOut1InBogus()))
        self.assertEqual(response.body.loopback[0].sink, "VA_AUDOUT_1")
        self.assertEqual(response.body.loopback[0].source, "")
        self.assertEqual(response.body.loopback[0].state, AnalogAudioResponse.DISCONNECTED)

        log.info("==== Test complete ====")

    ## Valid Test Case: Connect All In to Out 1, Report on all Out after Connect,
    #                   Disconnect All Out, Report on all Out after Disconnect
    #  Asserts:
    #       sink    == "VA_AUDOUT_6"
    #       source  == "PA_70V_AUDIN_1"
    #       state   == CONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_6"
    #       source  == "PA_70V_AUDIN_1"
    #       state   == CONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_6"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    #       sink    == "VA_AUDOUT_6"
    #       source  == ""
    #       state   == DISCONNECTED
    #       ---------------------
    def test_all(self):
        log = self.__class__.log
        module = self.__class__.module

        log.info("**** Valid Test Case: Connect All In to Out 1 ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.connectAll()))
        self.assertEqual(response.body.loopback[5].sink, "VA_AUDOUT_6")
        self.assertEqual(response.body.loopback[5].source, "PA_70V_AUDIN_1")
        self.assertEqual(response.body.loopback[5].state, AnalogAudioResponse.CONNECTED)

        log.info("**** Valid Test Case: Report on all Out after Connect ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.reportAll()))
        self.assertEqual(response.body.loopback[5].sink, "VA_AUDOUT_6")
        self.assertEqual(response.body.loopback[5].source, "PA_70V_AUDIN_1")
        self.assertEqual(response.body.loopback[5].state, AnalogAudioResponse.CONNECTED)

        log.info("**** Valid Test Case: Disconnect All Out ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.disconnectAll()))
        self.assertEqual(response.body.loopback[5].sink, "VA_AUDOUT_6")
        self.assertEqual(response.body.loopback[5].source, "")
        self.assertEqual(response.body.loopback[5].state, AnalogAudioResponse.DISCONNECTED)

        log.info("**** Valid Test Case: Report on all Out after Disconnect ****")
        response = module.msgHandler(ThalesZMQMessage(AnalogAudioMessages.reportAll()))
        self.assertEqual(response.body.loopback[5].sink, "VA_AUDOUT_6")
        self.assertEqual(response.body.loopback[5].source, "")
        self.assertEqual(response.body.loopback[5].state, AnalogAudioResponse.DISCONNECTED)

        log.info("==== Test complete ====")

if __name__ == '__main__':
    unittest.main()

## @endcond
