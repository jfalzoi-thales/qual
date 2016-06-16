# Memory Bandwidth Module
The Memory Bandwidth function is not a test in itself but rather a mechanism for measuring the memory bandwidth under the test conditions.				

##### Memory Bandwidth Request:
The Memory Bandwidth Request Message is sent by the TE to run or stop the application and request the memory bandwidth statistics.  
If	a	report	request	is	sent	the	reply	is	a	report	without	changing	the	
application	state. 

  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2};
  - required RequestTypeT requestType = 1 [default = OFF];
  
##### Memory Bandwidth Response:  
  - enum AppStateT {STOPPED=0; RUNNING=1}
  - required RequestTypeT requestType = 1 [default = STOP];
  - required float memoryBandWidth = 2;