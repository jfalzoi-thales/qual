# ARINC-429 Module
The purpose of the ARINC 429 Application is to simulate loading of the ARINC 429 bus components and detect failures thereof.  
The test strategy is to generate output on the transmitter channels (connection source) which will be externally looped back  
to the input channels (connection sink) in order to load and verify	both the transmitter and receiver circuits.  
The TE will provide the MPS with the loopback mapping according to the test procedure.  
Note that the MPS will allow a source to have multiple connections so that a source can be looped back to more than one sink.  
A sink, however, can have only one connection and therefore only one source.  
 
##### ARINC 429 Request:
The ARINC 429 Request Message is sent by the TE to establish or remove a loopback connection, or request a report for the sink.  
For each connection, the MPS will transmit a test pattern on the source channel and compare the data received on the connected sink channel.  
The TE may also request a report, in which case the MPS will respond with the status of the specified sink.  
  
  - enum RequestTypeT {DISCONNECT= 0; CONNECT= 1; REPORT= 2};
  - required RequestTypeT requestType = 1 [default = DISCONNECT];
  - required string sink = 2 [default = “”];
  - optional string source = 3 [default = “”];
  
##### ARINC 429 Response:  
  - enum ConStateT {DISCONNECTED = 0; CONNECTED = 1};
  - message StatusMessage {required string sink=1; required string source=2 [default = “”]; required ConStateT conState=3; required uint32 xmtCount=4; required uint32 rcvCount=5; required uint32 errorCount=6}
  - repeated StatusMessage status = 1;