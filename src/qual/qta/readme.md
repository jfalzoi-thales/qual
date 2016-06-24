# Qual Test App (QTA) {#QTAReadme}

MPS Qualification Test Application (QTA)
========================================

The MPS Qualification Test Application is the shell within which all of the
various test modules run.  It sets up the ZeroMQ request ports, and hands
off incoming requests to the appropriate module for handling.

### Service connections

The external Test Equipment (TE) software communicates with the Qualification
Test Software (Qual) via an Ethernet interface.   Transactions between the TE
and Qual are based on the client-server model implemented using the ZeroMQ (ZMQ)
embeddable networking library.  The ZMQ Request-Reply model is used, with the
Qual software acting as the server, receiving requests from the TE, and returning
replies back to the TE.

The MPS Qualification Software test application exposes two TCP ports for ZMQ 
messaging:

 * Port 50001 accepts messages and returns replies encoded in GPB format, as defined in the “Thales Common Network Messaging ICD” document.  These are ZMQ multipart messages with 3 frames:
   + Frame 0 contains the message name, as a string
   + Frame 1 contains a message header in GPB binary format (currently ignored by the MPS Qualification software)
   + Frame 2 contains the message body in GPB binary format
 * Port 50002 accepts messages and returns replies encoded in JSON format.  These are ZMQ multipart messages with 2 frames:
   + Frame 0 contains the message name, as a string
   + Frame 1 contains the JSON-encoded message, as a string

The ZMQ service addresses for both the GPB and JSON listeners can be configured in the MPS Qualification Software configuration file, located at `qual/config/platform.ini` in the MPS Qualification Software installation directory.  The parameter names and their default values are shown below.

    [QualTestApp]
    gpbServiceAddress  = tcp://*:50001
    jsonServiceAddress = tcp://*:50002

