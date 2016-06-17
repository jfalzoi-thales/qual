# Host Domain Device Service module
The Host Domain Device Service (HDDS) module provides a pass-through interface to
the Host Domain Device Service running on the MPS.  It uses the same request and
reply message types as the HDDS itself.

##### HDDS Get Request:
GetReq is a client request to HDDS for one or more elements by key name.

  - repeated string key = 1;
  
##### HDDS Get Response:
GetResp is the response for GetReq message and contains a ValueResp for each
key/value pair provided in the request message.

  - repeated ValueResp values = 1;

ValueResp is is used to communicate a key/value pair response along with
notification of the success in obtaining the requested key:

  - required bool success = 1;
  - required Property keyValue = 2;
  - optional ErrorMessage error = 3;

Property is is used for defining a key/value pair and has the following structure:

  - required string key = 1;
  - required string value = 2;

ErrorMessage is is used for communicating a descriptive error with code and has
the following structure:

  - required uint32 error_code = 1;
  - optional string error_description = 2;

##### HDDS Set Request:
SetReq is is a request message to HDDS to set given key(s) to the given value(s).

  - repeated Property values = 1;

See above for the definition of Property.

##### HDDS Set Response:
HDDSSetResp is the response for a SetReq message and contains a ValueResp for each
key/value pair provided in the request message.

  - repeated ValueResp values = 1;

See above for the definition of ValueResp.
