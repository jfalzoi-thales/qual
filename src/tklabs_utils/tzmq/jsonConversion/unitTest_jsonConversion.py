import unittest

# @TODO Fix these imports intuitively
from common.pb2.PowerInfo_pb2 import PowerInfo
from qual.pb2.CPULoading_pb2 import CPULoadingRequest
from qual.pb2.HDAudio_pb2 import HDAudioRequest
from qual.pb2.HDDS_pb2 import GetResp
from tklabs_utils.tzmq.jsonConversion.jsonConversion import JsonConversion

# @cond doxygen_unittest

class TestJsonConverstion(unittest.TestCase):

    def test_basic(self):
        message = CPULoadingRequest()

        message.requestType = CPULoadingRequest.RUN
        message.level = 50

        messageName, json = JsonConversion.gpb2json(message)
        newMessage = JsonConversion.json2gpb(messageName, json)

        self.assertEqual(message.level, newMessage.level)
        self.assertEqual(message.requestType, newMessage.requestType)

    def test_enumStringFloat(self):
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.CONNECT
        message.source = 'foo'
        message.volume = 10.1

        messageName, json = JsonConversion.gpb2json(message)
        newMessage = JsonConversion.json2gpb(messageName, json)

        self.assertEqual(message.requestType, newMessage.requestType)
        self.assertEqual(message.source, newMessage.source)
        self.assertEqual(message.volume, newMessage.volume)

    def test_defaultValue(self):
        message = HDAudioRequest()
        message.requestType = HDAudioRequest.CONNECT
        message.volume = 10.1

        messageName, json = JsonConversion.gpb2json(message)
        newMessage = JsonConversion.json2gpb(messageName, json)

        self.assertEqual(message.requestType, newMessage.requestType)
        self.assertEqual(u'', newMessage.source)
        self.assertEqual(message.volume, newMessage.volume)


    def test_listMessages(self):
        message = PowerInfo()
        message.errorCode = PowerInfo.I2C_MGR_CONN_ERROR

        for index in range(5) :
            newValue = message.values.add()
            newValue.name = 'Name_%d' % (index,)
            newValue.key = 'Key_%d' % (index,)
            newValue.value = 'Value_%d' % (index,)

        messageName, json = JsonConversion.gpb2json(message)
        newMessage = JsonConversion.json2gpb(messageName, json)

        self.assertEqual(message.errorCode, newMessage.errorCode)
        self.assertEqual(len(message.values), 5)
        self.assertEqual(message.values[3].name, 'Name_3')

    def test_subMessage(self):
        message = SystemMonitoringResponse()
        message.switchData.statistics.append("SUPER SECRET STATISTICS")
        message.switchData.statistics.append("MORE SECRET STATISTICS")
        message.switchData.temperature = "10,000,000 degrees"

        messageName, json = JsonConversion.gpb2json(message)
        newMessage = JsonConversion.json2gpb(messageName, json)
        self.assertEqual(newMessage.switchData.temperature, "10,000,000 degrees")
        self.assertEqual(len(newMessage.switchData.statistics), 2)
        self.assertEqual(newMessage.switchData.statistics[0], "SUPER SECRET STATISTICS")
        self.assertEqual(newMessage.switchData.statistics[1], "MORE SECRET STATISTICS")

        return

    def test_HDDSResp1(self):
        message = GetResp()
        valueResp = message.HDDSValue.add()
        valueResp.value.key = "k"
        valueResp.value.value = "v"
        valueResp.success = False
        valueResp.error.error_code = 1001
        valueResp.error.description = "error"

        messageName, json = JsonConversion.gpb2json(message)
        newMessage = JsonConversion.json2gpb(messageName, json)
        newValue = newMessage.HDDSValue[0]
        self.assertEqual(newValue.value.key, "k")
        self.assertEqual(newValue.value.value, "v")
        self.assertFalse(newValue.success)
        self.assertEqual(newValue.error.error_code, 1001)
        self.assertEqual(newValue.error.description, "error")

    def test_HDDSResp2(self):
        message = GetResp()
        valueResp = message.HDDSValue.add()
        valueResp.value.key = "k"
        valueResp.value.value = "v"
        valueResp.success = False

        messageName, json = JsonConversion.gpb2json(message)
        newMessage = JsonConversion.json2gpb(messageName, json)
        newValue = newMessage.HDDSValue[0]
        self.assertEqual(newValue.value.key, "k")
        self.assertEqual(newValue.value.value, "v")
        self.assertFalse(newValue.success)


        return




if __name__ == '__main__':
    unittest.main()
## @endcond
