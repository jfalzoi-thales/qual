import unittest
from common.gpb.jsonConversion.jsonConversion import JsonConversion
from common.gpb.python.CPULoading_pb2 import CPULoadingRequest
from common.gpb.python.HDAudio_pb2 import HDAudioRequest
from common.gpb.python.PowerInfo_pb2 import PowerInfo

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



if __name__ == '__main__':
    unittest.main()
## @endcond
