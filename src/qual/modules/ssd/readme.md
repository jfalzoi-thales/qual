# SSD Application

##### SSD Application Request:
The SSDRequest Message is sent by the TE to initiate or halt the SSD application according to the test procedure.	

  - enum RequestTypeT {STOP=0; RUN=1};
  - required RequestTypeT requestType = 1 [default = STOP];
  
##### SSD Application Response:
The SSDResponse Message is sent by the MPS to acknowledge an SSD Application request or report an error.  

  - enum AppStateT {STOPPED=0; RUNNING=1};
  - required AppStateT state = 1;