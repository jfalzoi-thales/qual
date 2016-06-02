System Module Diagram
---------------------
![System Modules](design.png "Modules")


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
