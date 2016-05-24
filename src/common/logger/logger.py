import logging

#https://docs.python.org/2/howto/logging.html#logging-basic-tutorial
class Logger(logging.getLoggerClass()):

    def __init__(self, name):
        super(Logger, self).__init__(name)
        self.formatChannel()

    def formatChannel(self):
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.addHandler(ch)


    pass
