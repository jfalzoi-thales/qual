HD Audio Module
===============
The	HD Audio Application consists of the MPS outputting analog audio signals by converting the specified digital source	through	the	Carrier	Card HD Audio Codec.

##### HD Audio Request
  - enum RequestTypeT {DISCONNECT=0; CONNECT=1; REPORT=2}
  - required RequestTypeT requestType = 1 [default = DISCONNECT];
  - optional string source = 2 [default = ""];
  - optional float volume = 3;
  
##### HD Audio Response
  - enum AppStateT {DISCONNECTED=0; CONNECTED=1}  
  - required AppStateT appState = 1 [default = DISCONNECTED];
  - required string source = 2 [default=""]
  - required float volume = 3;