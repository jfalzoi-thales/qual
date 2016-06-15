RS-485 Module
=============
RS-485 Application simulates loading of the RS-485 bus components and detect any failures thereof.  
The test strategy is to generate output on the RS-485 channel which will be externally echoed by the TE back  
to the MPS RS-485 channel in order to load and verify both the transmitter and receiver circuits.  
The transmitted and received data are then compared and mismatches reported.

##### RS-485 Request Message
  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2}
  - required RequestTypeT requestType = 1 [default = STOP];

##### RS-485 Response Message
  - enum AppStateT {STOPPED=0; RUNNING=1}
  - required AppStateT state = 1;
  - required uint32 matches = 2 [default = 0];
  - required uint32 mismatches = 3 [default = 0];