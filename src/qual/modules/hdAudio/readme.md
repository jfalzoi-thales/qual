# Carrier Card HD Audio Module
The HD Audio Application consists of the MPS outputting analog audio signals by converting the specified digital source through the Carrier Card HD Audio Codec.		

##### HD Audio Request:
The HD Audio Request Message is sent by the TE to start or stop the HD Audio Application.  
The optional source string consists of a path/filename to which the HD Audio Application has access.  
If the CONNECT request does not include the optional source string, a default file will be used.  
If the DISCONNECT request includes the optional source string, the string is ignored.  
If the optional volume parameter is included the output volume will be set accordingly.  

  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2};
  - required RequestTypeT requestType = 1 [default = OFF];
  - required string local = 2 [default = “”];
  - optional string remote = 3 [default = “”];
  
##### HD Audio Response:  
  - enum AppStateT {STOPPED=0; RUNNING=1}
  - required AppStateT state = 1;
  - required string source = 2 [default = ""];
  - required string volume = 3;