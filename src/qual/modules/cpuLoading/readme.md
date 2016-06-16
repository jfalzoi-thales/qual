# CPU Loading Module
The CPU Loading function is not a test in itself but rather a mechanism to achieve a configurable percentage of CPU utilization.  
The goal is to establish a nominal load on the LRU while testing other aspects of the product.  
 
##### CPU Loading Request:
The CPU Loading Request Message is sent by the TE to run or stop the CPU loading function and request a report of the current  
state of the application and latest processor utilization statistics. If a report request is sent the reply is a report without  
changing the application state. The optional level message element sets the desired loading level in percentage of total  
CPU utilization (default 80%).  

  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2};
  - required RequestTypeT requestType = 1 [default = STOP];
  - optional float level;
  
##### CPU Loading Response:  
  - enum AppStateT {STOPPED=0; RUNNING=1}
  - required AppStateT state = 1;
  - required float totalUtilization = 2;
  - repeated float coreUtilization = 3;