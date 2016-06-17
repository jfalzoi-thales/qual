# Host Domain Device Service Module
The Host Domain Device Service (HDDS) module provides a pass-through interface to
the Host Domain Device Service running on the MPS.  It uses the same request and
reply message types as the HDDS itself.

##### HDDS Get Request:
GetReq is a client request to HDDS for one or more elements by key name:

  - repeated string key = 1;
  
##### HDDS Get Response:
GetResp is the response for GetReq message and contains a ValueResp for each
key/value pair provided in the request message:

  - repeated ValueResp HDDSValue = 1;

ValueResp is is used to communicate a key/value pair response along with
notification of the success in obtaining the requested key:

  - required bool success = 1;
  - optional ErrorMsg error = 2;
  - optional Property value = 3;

Property is is used for defining a key/value pair:

  - required string key = 1;
  - required string value = 2;

ErrorMsg is is used for communicating a descriptive error with code:

  - required uint32 error_code = 1;
  - optional string description = 2;

##### HDDS Set Request:
SetReq is is a request message to HDDS to set given key(s) to the given value(s):

  - repeated Property HDDSValue = 1;

See above for the definition of Property.

##### HDDS Set Response:
SetResp is the response for a SetReq message and contains a ValueResp for each
key/value pair provided in the request message:

  - repeated ValueResp HDDSValue = 1;

See above for the definition of ValueResp.
