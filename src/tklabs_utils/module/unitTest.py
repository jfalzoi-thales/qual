import unittest
from time import sleep

from tklabs_utils.logger.logger import Logger
from tklabs_utils.module.module import Module


# @cond doxygen_unittest


class BaseMessage(object):
    pass


class RequestReportMessage(BaseMessage):
    def __init__(self):
        self.response = False
        self.counter = 0
        super(RequestReportMessage, self).__init__()

class MessageContainer(object):
    def __init__(self, body):
        self.body =body


class Example(Module):

    def __init__(self, config=None):
        super(Example, self).__init__(config)
        self.interval = 0
        self.counter = 0
        self.loadConfig(attributes=('interval',))
        self.addMsgHandler(RequestReportMessage, self.report)
        self.addThread(self.runCounter1)

    @classmethod
    def getConfigurations(cls):
        return ('Example', 'Example2')

    #Thread Execution function, must return quickly
    def runCounter1(self):
        self.counter += 1
        sleep(self.interval/1000.0)
        self.log.debug('counter now %d' % (self.counter))
        return

    def report(self, msg):
        msg.response = True
        msg.counter = self.counter
        return MessageContainer(body=msg)



class Test_Module(unittest.TestCase):

    def setUp(self):
        self.log = Logger(name=self._testMethodName)

    def test_config(self):
        module1 = Example(config=Example.getConfigurations()[0])
        module2 = Example(config=Example.getConfigurations()[1])
        self.assertEqual(module1.interval, 1000)
        self.assertEqual(module2.interval, 2000)

    def test_message(self):
        module1 = Example(config=Example.getConfigurations()[0])
        msg = MessageContainer(body=RequestReportMessage())
        self.assertFalse(msg.body.response)
        status = module1.msgHandler(msg)
        self.assertTrue(status.body.response)

    def test_lock(self):
        module1 = Example(config=Example.getConfigurations()[0])
        module2 = Example(config=Example.getConfigurations()[1])
        lock1 = module1.getNamedLock("Test")
        lock2 = module2.getNamedLock("Test")
        self.assertEqual(lock1, lock2)

    def test_thread(self):
        testSeconds = 10
        module1 = Example(config=Example.getConfigurations()[0])
        module1.startThread()
        sleep(testSeconds)
        module1.stopThread()
        msg = MessageContainer(body=RequestReportMessage())
        self.assertFalse(msg.body.response)
        status = module1.msgHandler(msg)
        self.assertTrue(status.body.response)
        self.assertEqual(status.body.counter, testSeconds)

        #Make sure it stopped
        sleep(5)
        msg = MessageContainer(body=RequestReportMessage())
        status = module1.msgHandler(msg)
        self.assertEqual(status.body.counter, testSeconds)





if __name__ == '__main__':
    unittest.main()
## @endcond
