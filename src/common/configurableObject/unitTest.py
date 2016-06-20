import unittest
from common.configurableObject.configurableObject import ConfigurableObject


class TestObject1(ConfigurableObject):

    @classmethod
    def getConfigurations(cls):
        return ['test_multi1', 'test_multi2' ]

    def __init__(self, config=None):

        super(TestObject1, self).__init__(config)

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
        testObject = TestObject1() #Use testObject1 as the INI Section Name
        self.assertTrue(testObject.bool1)
        self.assertTrue(testObject.bool2)
        self.assertTrue(testObject.bool3)
        self.assertEqual(testObject.float1, 7.0)
        self.assertEqual(testObject.int1, 42)
        self.assertEqual(testObject.string1, 'Goodbye')

    def test_customConfig(self):
        testObject = TestObject1(self._testMethodName) #Use the test case name as the INI Section Name
        self.assertTrue(testObject.bool1)
        self.assertTrue(testObject.bool2)
        self.assertTrue(testObject.bool3)
        self.assertEqual(testObject.float1, 7.1)
        self.assertEqual(testObject.int1, 43)
        self.assertEqual(testObject.string1, 'Hello World!')


    def test_MultipleConfigs(self):
        for config in TestObject1.getConfigurations():
            testObject = TestObject1(config=config)
            if config == 'test_multi1' :
                self.assertEqual(testObject.int1, 44)
            else:
                self.assertEqual(testObject.int1, 45)



if __name__ == '__main__':
    unittest.main()
