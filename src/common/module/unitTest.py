import unittest
from time import sleep

from src.common.module.module import Module

class Example(Module):

    #Thread Setup Function
    # e.g. Setup member variables
    def setup(self):
        self.counter = 0
        print 'Example setup'
        pass

    # Thread Cleanup function
    #
    def cleanup(self):
        print 'Example cleanup'
        pass

    #Thread Execution function
    def run(self):
        self.counter += 1
        #self.log(self.DEBUG, 'counter now %d' % (self.counter))
        return

    def message(self, msg):
        return self.counter


class Test_Module(unittest.TestCase):

    def setUp(self):
        self.module = Example(config={})
        print 'setup My Test'

    def tearDown(self):
        print 'teardown My test'
        self.module.terminate()
        pass

    def test_basic(self):

        print 'Test 1'
        for loop in range(10) :
            sleep(1)
            print 'Counter returns', self.module.message(None)

        pass

    def test_basic2(self):
        print 'Test 2'
        pass

if __name__ == '__main__':
    unittest.main()
