import unittest
from common.configurableObject.configurableObject import ConfigurableObject


class testObject1(ConfigurableObject):
    def __init__(self, config=None):

        super(testObject1, self).__init__(config)

        self.int1 = 5
        self.string1 = 'Hello'
        self.float1 = 0.5
        self.bool1 = False
        self.bool2 = False
        self.bool3 = False
        self.loadConfig(attributes=('int1', 'string1', 'float1', 'bool1', 'bool2', 'bool3'))
        return

class Test_ConfigurableObject(unittest.TestCase):

    def test_basic(self):
        testObject = testObject1()
        self.assertTrue(testObject.bool1)
        self.assertTrue(testObject.bool2)
        self.assertTrue(testObject.bool3)
        self.assertEqual(testObject.float1, 7.0)
        self.assertEqual(testObject.int1, 42)
        self.assertEqual(testObject.string1, 'Goodbye')

    def test_customConfig(self):
        testObject = testObject1(self._testMethodName)
        self.assertTrue(testObject.bool1)
        self.assertTrue(testObject.bool2)
        self.assertTrue(testObject.bool3)
        self.assertEqual(testObject.float1, 7.1)
        self.assertEqual(testObject.int1, 43)
        self.assertEqual(testObject.string1, 'Hello World!')



if __name__ == '__main__':
    unittest.main()
