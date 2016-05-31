System Module Diagram
---------------------
![System Modules](design.png "Modules")

Requirements & Design
---------------------
The QUAL system is functionally split into the following functional areas

- GPB Message Buffers
    + Based on Thales ICD Specifications :  [Overall Specification](file://something.pdf)
    + Implemented to GPB standards: [reference](https://developers.google.com/protocol-buffers/)
    + [Read About Generating GPB Files](@ref GPBBufferReadme)
- ZeroMQ Message Queues
    + say something
- QTA Test Application Interface
    + say something
- QUAL Test Modules
    + Say something?


System Startup
--------------
The QTA, when launched, will self-discover all test modules that are present & available.  Once the modules are detected they
will be configured and ready to receive GPB-based message buffers, implementing the published Thales ICD specifications.

~~~~
    Add the commandline here
~~~~

Console-Based QTE Simulator
---------------------------
For testing purposes, a console-based simulated QTE has been created.  This QTE uses the GPB buffers and ZMQ implementations and exactly mimics expected QTE communication. 

~~~~
    Add the commandline here
~~~~
