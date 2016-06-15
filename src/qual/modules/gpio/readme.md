# Module - GPIO {#ModuleGPIOReadme}

Description
===========

The GPIO module covers exercising MPS general purpose discrete inputs and
outputs.  During testing, the MPS hardware will be configured with certain
GPIO output pins connected to GPIO input pins.  The TE then sends loopback
connection requests to the module which reflect the hardware connections.

When an output pin is connected the module will assert and de-assert the output
pin with the expectation of sensing the same state on the input pin.
The module maintains a count, for each loopback pin pair, of mismatches
defined as when the input pin state does not match the current state of the
associated output pin.


GPIO Request
============

The GPIO Request Message is sent by the TE to establish or remove a loopback 
connection, or request statistics regarding the connection.   

  * When the request type is __CONNECT__, the __gpIn__ parameter must be an 
    unconnected GP input and the __gpOut__ parameter must be a GP output.
    Any other combination will result in a response without establishing
    a connection (i.e. one output to multiple inputs is allowed but more
    than one output to one input is not.) 
  * When the request type is __DISCONNECT__, the connection between the
    __gpOut__ and __gpIn__ pins is removed. 
  * When the request type is __REPORT__, the connection for __gpIn__ is unchanged
    and the response message is sent. 

For all request types, if __gpIn__ is “ALL” then each input is connected to the
one __gpOut__, disconnected from its current output if any, or reported, as
appropriate for the request type.

The GPIO Request fields are as follows:

  * __requestType__: One of the following:
    + __STOP__: Requests the application to halt and reply with a report;
      report will include the counter values just prior to stopping 
    + __RUN__: Requests the application to run and reply with a report
    + __REPORT__: Requests the application to respond with a report
  * __gpIn__  	MPS discrete input
  * __gpOut__	MPS discrete output (ignored for DISCONNECT or REPORT)


GPIO Response
=============

The GPIO Response Message is sent to provide the connection state and loopback
statistics for one or more GPIO inputs. The GPIO Response contains one or more
__GpioStatus__ blocks, each describing the status of a GPIO input.  Each
__GpioStatus__ block contains:

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
