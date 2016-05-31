import unittest

from common.classFinder.classFinder import ClassFinder
from google.protobuf.message import Message


class TestStringMethods(unittest.TestCase):

    def test_findByName(self):

        classNames = (
            'RS232Request',
            'RS232Response',
            'EthernetResponse',
            'MemoryBandwidthResponse'

        )

        classFinder = ClassFinder(rootPath='common.gpb.python',
                                  baseClass=Message)

        for className in classNames :
            searchClass = classFinder.getClassByName(className)
            myMessage = searchClass()

            self.assertEqual(myMessage.__class__.__name__, className)
            print 'Message is a ', myMessage.__class__.__name__



if __name__ == '__main__':
    unittest.main()
