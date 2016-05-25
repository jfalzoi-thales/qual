import subprocess
import sys
from module import Module
from time import sleep
import zmq
import CPULoading_pb2
import CPULoader
import ThalesZMQMessage

## CPULoading Class Module
#
class CPULoading(Module):
    def __init__(self):
        super(CPULoading, self).__init__({})
        self.active = False
        self.loader = CPULoader.CPULoader()
        self.loader.start()
        self.addMsgHandler(CPULoading_pb2.CPULoadingRequest, self.handler)

    def handler(self, msg):
        reply = CPULoading_pb2.CPULoadingResponse()

        if msg.body.requestType == CPULoading_pb2.CPULoadingRequest.RUN:
            if msg.body.level != 0:
                print("start with level")
                reply = self.start(msg.body.level)
            else:
                print("start without level")
                reply = self.start()
        elif msg.body.requestType == CPULoading_pb2.CPULoadingRequest.STOP:
            reply = self.stop()
        elif msg.body.requestType == CPULoading_pb2.CPULoadingRequest.REPORT:
            reply = self.report()
        else:
            print("Unexpected Value")

        return reply

    def start(self, level = 80):
        self.active = True

        subprocess.Popen(["sudo", "pkill", "-9", "lookbusy"]).communicate()

        if level in range(0, 100):
            subprocess.Popen(["/usr/local/bin/lookbusy", "-qc", str(level)])
            sleep(1)
        else:
            print("Unexpected Value")

        return self.report()

    def stop(self):
        self.active = False
        subprocess.Popen(["sudo", "pkill", "-9", "lookbusy"]).communicate()

        return self.report()

    def report(self):
        results = self.loader.getcpuload()
        print(results)
        loadResponse = CPULoading_pb2.CPULoadingResponse()

        if self.active == True:
            loadResponse.state = CPULoading_pb2.CPULoadingResponse.RUNNING
        else:
            loadResponse.state = CPULoading_pb2.CPULoadingResponse.STOPPED

        if results != {}:
            loadResponse.totalUtilization = results["cpu"]

        for key, value in results.items():
            if key != "cpu":
                loadResponse.coreUtilization.append(value)

        return loadResponse

    def terminate(self):
        subprocess.Popen(["sudo", "pkill", "-9", "lookbusy"]).communicate()
        self.loader.quit = True
        self.active = False
        sleep(2)
        sys.exit()

if __name__=='__main__':
    test = CPULoading()

    message = CPULoading_pb2.CPULoadingRequest()
    message.requestType = CPULoading_pb2.CPULoadingRequest.RUN
    message.level = 50
    request = ThalesZMQMessage.ThalesZMQMessage("CPULoading_pb2.CPULoadingRequest", message)

    test.handler(request)

    message2 = CPULoading_pb2.CPULoadingRequest()
    message2.requestType = CPULoading_pb2.CPULoadingRequest.REPORT
    request = ThalesZMQMessage.ThalesZMQMessage("CPULoading_pb2.CPULoadingRequest", message2)

    sleep(5)
    test.handler(request)

    test.terminate()