# GPIO Module

The GPIO module covers exercising MPS general purpose discrete inputs and
outputs.  During testing, the MPS hardware will be configured with certain
GPIO output pins connected to GPIO input pins.  The TE then sends loopback
connection requests to the module which reflect the hardware connections.

When an output pin is connected the module will assert and de-assert the output
pin with the expectation of sensing the same state on the input pin.
The module maintains a count, for each loopback pin pair, of mismatches
defined as when the input pin state does not match the current state of the
associated output pin.


##### GPIO Request
The GPIO Request Message is sent by the TE to establish or remove a loopback 
connection, or request statistics regarding the connection:

  - required RequestTypeT requestType = 1 [default = DISCONNECT];
  - required string gpIn  = 2 [default = ""];
  - optional string gpOut = 3 [default = ""];

The behavior is as follows:

  * When the request type is __CONNECT__, the __gpIn__ parameter must be an 
    unconnected GP input and the __gpOut__ parameter must be a GP output.
    Any other combination will result in a response without establishing
    a connection (i.e. one output to multiple inputs is allowed but more
    than one output to one input is not.) 
  * When the request type is __DISCONNECT__, the connection between the
    __gpOut__ and __gpIn__ pins is removed. 
  * When the request type is __REPORT__, the connection for __gpIn__ is unchanged
    and the response message is sent. 
  * For all request types, if __gpIn__ is “ALL” then each input is connected to the
    one __gpOut__, disconnected from its current output if any, or reported, as
    appropriate for the request type.

##### GPIO Response
The GPIO Response Message is sent to provide the connection state and loopback
statistics for one or more GPIO inputs: 

  - repeated GpioStatus status = 1;

Each GpioStatus block describes the status of a GPIO input:

  - required ConStateT conState = 1;
  - required int32 matchCount = 2;
  - required int32 mismatchCount = 3;
  - required string gpIn = 4;
  - optional string gpOut = 5;

The GpioStatus fields are as follows:

  * __conState__: One of the following:
    + __DISCONNECTED__ when the reply is generated the connection does not exist
    + __CONNECTED__ When the reply is generated the connection exists
  * __matchCount__: The number of matches for the specified connection since
    the last connection request for the pin pair, or zero if the connection
    does not exist.
  * __mismatchCount__: The number of mismatches for the specified connection
    since the last connection request for the pin pair, or zero if the
    connection does not exist.
  * __gpIn__: MPS discrete input 
  * __gpOut__: MPS discrete output, if a connection exists
