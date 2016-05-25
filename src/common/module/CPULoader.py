from time import sleep
import threading
lock = threading.Lock()

## CPULoader Class
#
class CPULoader(threading.Thread):
    def __init__(self, sleeptime = 1):
        threading.Thread.__init__(self)
        self.sleeptime = sleeptime
        self.cpuload = {}
        self.quit = False

    def getcputime(self):
        '''
        http://stackoverflow.com/questions/23367857/accurate-calculation-of-cpu-usage-given-in-percentage-in-linux
        read in cpu information from file
        The meanings of the columns are as follows, from left to right:
            0cpuid: number of cpu
            1user: normal processes executing in user mode
            2nice: niced processes executing in user mode
            3system: processes executing in kernel mode
            4idle: twiddling thumbs
            5iowait: waiting for I/O to complete
            6irq: servicing interrupts
            7softirq: servicing softirqs

        #the formulas from htop 
             user    nice   system  idle      iowait irq   softirq  steal  guest  guest_nice
        cpu  74608   2520   24433   1117073   6176   4054  0        0      0      0


        Idle=idle+iowait
        NonIdle=user+nice+system+irq+softirq+steal
        Total=Idle+NonIdle # first line of file for all cpus

        CPU_Percentage=((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)
        '''
        cpu_infos = {} #collect here the information
        with open('/proc/stat', 'r') as f_stat:
            lines = [line.split(' ') for content in f_stat.readlines() for line in content.split('\n') if line.startswith('cpu')]

            #compute for every cpu
            for cpu_line in lines:
                if '' in cpu_line: cpu_line.remove('')#remove empty elements
                cpu_line = [cpu_line[0]]+[float(i) for i in cpu_line[1:]]#type casting
                cpu_id,user,nice,system,idle,iowait,irq,softrig,steal,guest,guest_nice = cpu_line

                Idle = idle + iowait
                NonIdle = user + nice + system + irq + softrig + steal

                Total = Idle + NonIdle
                #update dictionary
                cpu_infos.update({cpu_id:{'total':Total,'idle':Idle}})
            return cpu_infos

    def getcpuload(self):
        lock.acquire()
        load = self.cpuload
        lock.release()
        return load

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