from time import sleep
import threading

## CPULoader Class
class CPULoader(threading.Thread):
    ## Constructor
    #  @param   self
    #  @param   sleeptime   Number of seconds to sleep DEFAULT = [1]
    def __init__(self, sleeptime = 1):
        # Initializes threading
        threading.Thread.__init__(self)
        ## Lock for preventing threading issues
        self.lock = threading.Lock()
        ## Stores sleeptime in seconds
        self.sleeptime = sleeptime
        ## Initializes cpuload
        self.cpuload = {}
        ## Thread exits when self.quit = True
        self.quit = False

    ## Grabs CPU usage statistics from Linux
    #  Retreives CPU usage information from '/proc/stat' and parses necessary information
    #  @param   self
    #  @return  cpu_infos   Dictionary containing CPU readings
    def getcputime(self):
        cpu_infos = {}

        with open('/proc/stat', 'r') as f_stat:
            #  Parses Linux CPU usage data from stat file
            lines = []

            for content in f_stat.readlines():
                for line in content.split('\n'):
                    if line.startswith('cpu'):
                        lines.append(line.split(' '))

            #  Compute CPU usage data for each core
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
    #  Polls thread for cpuload once lock has been acquired
    #  @param   self
    #  @return  load  Dictionary containing CPU load information
    def getcpuload(self):
        self.lock.acquire()
        load = self.cpuload
        self.lock.release()
        return load

    ## Calculates CPU Load
    #  Overrides run() method in Thread
    #  Uses the raw values obtained from self.getcputime() function and calculates CPU load percentages
    #  @param     self
    def run(self):
        start = self.getcputime()

        while not self.quit:
            sleep(self.sleeptime)
            stop = self.getcputime()
            self.lock.acquire()

            for cpu in start:
                Total = stop[cpu]['total']
                PrevTotal = start[cpu]['total']
                Idle = stop[cpu]['idle']
                PrevIdle = start[cpu]['idle']
                CPU_Percentage = ((Total - PrevTotal) - (Idle - PrevIdle)) / (Total - PrevTotal) * 100
                self.cpuload[cpu] = CPU_Percentage

            self.lock.release()
            start = stop