SSD Module
==========
The purpose of the SSD Utilization Application is to exercise the SSD RAID.  
The SSD Utilization function consists of invoking the FIO test program and reporting the results.

##### SSD Request Message
  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2}
  - required RequestTypeT requestType = 1 [default = STOP];

##### SSD Response Message
  - enum AppStateT {STOPPED=0; RUNNING=1}
  - required AppStateT state = 1;