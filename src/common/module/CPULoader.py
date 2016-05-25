from time import sleep
import threading

lock = threading.Lock()

## CPULoader Class
#
class CPULoader(threading.Thread):
    ## Constructor
    #  @param     self
    #  @param     sleeptime     number of seconds to sleep DEFAULT = [1]
    def __init__(self, sleeptime = 1):
        ## initializes threading
        threading.Thread.__init__(self)
        ## stores sleeptime in seconds
        self.sleeptime = sleeptime
        ## initializes cpuload
        self.cpuload = {}
        ## thread exits when self.quit = True
        self.quit = False

    ## Grabs CPU usage statistics from Linux
    #
    #  Retreives CPU usage information from '/proc/stat' and parses necessary information
    #
    #  @param     self
    #  @return    cpu_infos     dictionary containing CPU readings
    def getcputime(self):
        cpu_infos = {}

        with open('/proc/stat', 'r') as f_stat:
            lines = [line.split(' ') for content in f_stat.readlines() for line in content.split('\n') if line.startswith('cpu')]

            for cpu_line in lines:
                if '' in cpu_line: cpu_line.remove('')
                cpu_line = [cpu_line[0]]+[float(i) for i in cpu_line[1:]]
                cpu_id,user,nice,system,idle,iowait,irq,softrig,steal,guest,guest_nice = cpu_line

                Idle = idle + iowait
                NonIdle = user + nice + system + irq + softrig + steal

                Total = Idle + NonIdle
                cpu_infos.update({cpu_id:{'total':Total,'idle':Idle}})

            return cpu_infos

    ## Returns CPU Load information
    #
    #  Polls thread for cpuload once lock has been acquired
    #
    #  @param     self
    #  @return    load  dict containing CPU load information
    def getcpuload(self):
        lock.acquire()
        load = self.cpuload
        lock.release()
        return load

    ## Calculates CPU Load
    #
    #  Overrides run() method in Thread
    #
    #  Uses the raw values obtained from self.getcputime() function and calculates CPU load percentages
    #
    #  @param     self
    def run(self):
        start = self.getcputime()

        while not self.quit:
            sleep(self.sleeptime)
            stop = self.getcputime()
            lock.acquire()

            for cpu in start:
                Total = stop[cpu]['total']
                PrevTotal = start[cpu]['total']
                Idle = stop[cpu]['idle']
                PrevIdle = start[cpu]['idle']
                CPU_Percentage = ((Total - PrevTotal) - (Idle - PrevIdle)) / (Total - PrevTotal) * 100
                self.cpuload[cpu] = CPU_Percentage
            lock.release()
            start = stop