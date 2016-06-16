# Ethernet Module

##### Ethernet Request:
The Ethernet Request Message is sent by the TE to set enable or disable performance statistic gathering on an Ethernet channel and obtain a statistics report.  
When the statistic gathering is active the MPS connects the local Ethernet channel to the remote iPerf server and collects performance statistics.  
If the optional remote server string is present, the remote server address is updated. If the request type is RUN and the remote address has not been set,  
the response is sent without starting the measurement.		

  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2};
  - required RequestTypeT requestType = 1 [default = OFF];
  - required string local = 2 [default = “”];
  - optional string remote = 3 [default = “”];
  
##### Ethernet Response:  
The Ethernet Response Message is sent by the MPS acknowledge an Ethernet Request message and provide statistics related to the iPerf measurement.  

  - enum AppStateT {STOPPED=0; RUNNING=1};
  - required AppStateT state = 1;
  - required string local = 2;
  - required string result = 3;