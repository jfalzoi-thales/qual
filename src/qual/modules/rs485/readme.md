# RS-485 Module
The purpose of the RS-485 Application is to simulate loading of the RS-485 bus components and detect any failures thereof.  
The test strategy is to generate output on the RS-485 channel which will be externally echoed by the TE back to the MPS RS-485  
channel in order to load and verify both the transmitter and receiver circuits.  
The transmitted and received data are then compared and mismatches reported.  

##### RS-485 Request:
The RS232Request Message is sent by the TE to initiate or halt transmission and verification of RS-485 data according to the test procedure.	

  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2};
  - required RequestTypeT requestType = 1 [default = STOP];
  
##### RS-485 Response:
The RS485Response Message is sent by the MPS to acknowledge an RS-485 request and provide the data mismatch statistics.  	

  - enum AppStateT {STOPPED=0; RUNNING=1}
  - required AppStateT state = 1;
  - required uint32 xmtCount = 2;
  - required uint32 matches = 3;
  - required uint32 mismatches = 4;