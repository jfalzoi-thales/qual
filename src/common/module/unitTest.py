import unittest
from time import sleep

from common.module.module import Module


class BaseMessage(object):
    pass

class StartMessage(BaseMessage):
    def __init__(self, interval):
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

    @classmethod
    def getConfigurations(cls):
        return [{'initial': 0},{'initial':2000}]

    #Thread Execution function, must return quickly
    def runCounter1(self):
        self.counter1 += 1
        sleep(self.interval/1000.0)
        #self.log('counter now %d' % (self.counter))
        return

    #Thread Execution function, must return quickly
    def runCounter2(self):
        self.counter2 += 11
        sleep(self.interval/10000.0)
        #self.log('counter now %d' % (self.counter))
        return


    #Thread Setup Function
    # e.g. Setup member variables, thread will be started in the Super
    def start(self, msg):
        self.counter1 = self.config['initial']
        self.counter2 = self.config['initial']
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
        print 'Test 1 - Run 1 Module with multiple Threads'
        self.module = Example(config=Example.getConfigurations()[0])
        self.module.msgHandler(StartMessage(interval=100))
        for loop in range(10) :
            sleep(1)
            status = self.module.msgHandler(RequestReportMessage())
            print 'Status reported as %d %d' % (status.value1, status.value2)
        self.module.msgHandler(StopMessage())
        pass

    def test_basic2(self):
        print 'Test 2 - Run Multiple Modules'
        configs = Example.getConfigurations()
        print 'There are %d configs' % (len(configs))
        modules = []
        for config in configs:
            module = Example(config=config)
            modules.append(module)

        for module in modules:
            module.msgHandler(StartMessage(interval=100))
        for loop in range(10) :
            sleep(1)
            print 'Looping--------->'
            for module in modules:
                status = module.msgHandler(RequestReportMessage())
                print 'Status reported as %d %d' % (status.value1, status.value2)
            print '<---------Looping'
        for module in modules:
            module.msgHandler(StopMessage())
        pass

if __name__ == '__main__':
    unittest.main()
