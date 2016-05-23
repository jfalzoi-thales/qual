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
    def __init__(self, value1, value2):
        self.value1 = value1
        self.value2 = value2
        super(StatusRequestMessage, self).__init__()
        pass


class Example(Module):

    def __init__(self, config={}):
        super(Example, self).__init__(config)
        self.addMsgHandler(StopMessage, self.stop)
        self.addMsgHandler(StartMessage, self.start)
        self.addMsgHandler(RequestReportMessage, self.report)
        self.addThread(self.runCounter1)
        self.addThread(self.runCounter2)

    #Thread Execution function, must return quickly
    def runCounter1(self):
        self.counter1 += 1
        sleep(self.interval/1000.0)
        #self.log('counter now %d' % (self.counter))
        return

    #Thread Execution function, must return quickly
    def runCounter2(self):
        self.counter2 += 11
        sleep(self.interval/1000.0)
        #self.log('counter now %d' % (self.counter))
        return



    #Thread Setup Function
    # e.g. Setup member variables, thread will be started in the Super
    def start(self, msg):
        self.counter1 = 0
        self.counter2 = 0
        self.interval = msg.interval
        super(Example, self).startThread()
        status = StatusRequestMessage(self.counter1,self.counter2)
        return status

    # Thread Cleanup function, thread will be stopped in the Super
    #
    def stop(self, msg):
        status = StatusRequestMessage(self.counter1,self.counter2)
        super(Example, self).stopThread()
        return status

    def report(self, msg):
        status = StatusRequestMessage(self.counter1,self.counter2)
        return status


class Test_Module(unittest.TestCase):

    def test_basic(self):
        print 'Test 1'
        self.module = Example()
        self.module.msgHandler(StartMessage(start=0, interval=100))
        for loop in range(10) :
            sleep(1)
            status = self.module.msgHandler(RequestReportMessage())
            print 'Status reported as %d %d' % (status.value1, status.value2)
        self.module.msgHandler(StopMessage())
        pass

    def test_basic2(self):
        print 'Test 2 - empty'
        pass

if __name__ == '__main__':
    unittest.main()
