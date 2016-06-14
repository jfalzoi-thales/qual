RS232 Module
============
RS-232 Application simulates loading of the RS-232 bus components and detect any failures thereof.  
The test strategy is to generate output on the transmitter channel which will be externally looped  
back to the receiver channel in order to load and verify both the transmitter and receiver circuits.

##### RS-232 Request Message
  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2}
  - required RequestTypeT requestType = 1 [default = STOP];

##### RS-232 Response Message
  - enum AppStateT {STOPPED=0; RUNNING=1}
  - required AppStateT state = 1;
  - required uint32 matches = 2 [default = 0];
  - required uint32 mismatches = 3 [default = 0];