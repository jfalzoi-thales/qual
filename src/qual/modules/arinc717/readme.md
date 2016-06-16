# ARINC-717 Module
The purpose of the ARINC 717 Application is to simulate loading of the ARINC 717 bus components and detect failures thereof.  
The test strategy is to externally generate data which is transmitted to the MPS ARINC 717 RX channel in order to load and verify the receiver circuit.  
The received data is output on the reporting interface for error checking. 	
 
##### ARINC 717 Frame Request:
The ARINC 717 Frame Request Message is sent by the TE to control the application state and to request the most recent ARINC 717 frame data and status.  
 
  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2};
  - required RequestTypeT requestType = 1 [default = STOP];
  
##### ARINC 717 Frame Response:  
  - enum AppStateT {STOPPED=0; RUNNING=1};
  - enum FrameSync {NO_SYNC=0; SYNCED=1};
  - required AppStateT state = 1;
  - required FrameSync syncState = 2 [default = NO_SYNC];
  - repeated int16 arinc717frame = 3;