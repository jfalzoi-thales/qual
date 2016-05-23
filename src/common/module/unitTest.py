import unittest
from time import sleep

from src.common.gpb.python.baseMessage import BaseMessage
from src.common.module.module import Module


class StartMessage(BaseMessage):
    def __init__(self, start, interval):
        self.start = start
        self.interval = interval
        super(StartMessage, self).__init__()

class StopMessage(BaseMessage):
    def __init__(self):
        super(StopMessage, self).__init__()
        pass

class RequestReportMessage(BaseMessage):
    def __init__(self):
        super(RequestReportMessage, self).__init__()
        pass

class StatusRequestMessage(BaseMessage):
    def __init__(self, value):
        self.value = value
        super(StatusRequestMessage, self).__init__()
        pass


class Example(Module):

    def __init__(self, config={}):
        super(Example, self).__init__(config)
        self.addMsgHandler(StopMessage, self.stop)
        self.addMsgHandler(StartMessage, self.start)
        self.addMsgHandler(RequestReportMessage, self.report)

    #Thread Execution function, must return quickly
    def run(self):
        self.counter += 1
        sleep(self.interval/1000.0)
        #self.log(self.DEBUG, 'counter now %d' % (self.counter))
        super(Example, self).run()

    #Thread Setup Function
    # e.g. Setup member variables, thread will be started in the Super
    def start(self, msg):
        self.counter = 0
        self.interval = msg.interval
        super(Example, self).startThread()
        status = StatusRequestMessage(self.counter)
        return status

    # Thread Cleanup function, thread will be stopped in the Super
    #
    def stop(self, msg):
        status = StatusRequestMessage(self.counter)
        super(Example, self).stopThread()
        return status

    def report(self, msg):
        status = StatusRequestMessage(self.counter)
        return status


class Test_Module(unittest.TestCase):

    def test_basic(self):
        print 'Test 1'
        self.module = Example()
        self.module.msgHandler(StartMessage(start=0, interval=100))
        for loop in range(10) :
            sleep(1)
            status = self.module.msgHandler(RequestReportMessage())
            print 'Status reported as %d' % (status.value)
        self.module.msgHandler(StopMessage())
        pass

    def test_basic2(self):
        print 'Test 2 - empty'
        pass

if __name__ == '__main__':
    unittest.main()
