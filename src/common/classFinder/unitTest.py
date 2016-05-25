import unittest

from common.classFinder.classFinder import ClassFinder
from google.protobuf.reflection import GeneratedProtocolMessageType


class TestStringMethods(unittest.TestCase):

    def test_findByName(self):

        classNames = (
            'RS232Request',
            'RS232Response',
            'EthernetResponse',
            'MemoryBandwidthResponse'

        )

        for className in classNames :
            classFinder= ClassFinder(rootPath='common.gpb',
                                     baseClass=GeneratedProtocolMessageType)
            searchClass = classFinder.getClassByName(className)
            myMessage = searchClass()

            self.assertEqual(myMessage.__class__.__name__, className)
            print 'Message is a ', myMessage.__class__.__name__



if __name__ == '__main__':
    unittest.main()