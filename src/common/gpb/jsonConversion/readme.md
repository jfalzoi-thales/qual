# GPB JsonConversion {#GPBJson}

GPB-JSON Serialization
======================

# Overview
The ICD Documents specify GPB protocol buffers, which are convertable to python classes, however
the QTE has requested the messages be delivered as JSON-encoded messages.  To keep the baked-in 
decision to use GPB protocol specifications internally and support JSON encoded externally, a
JSON-Serialization method for GPB buffers was required.

# JSON Format
The ICD documents specific Protcol Buffer prototypes.  To represent these prototypes in JSON, t
the following encoding rules are applied:

* All Field names are exactly how they appear in the prototype, including case
* All Enumerated values shall be represented as their String values, including case
* Repeated values shall be represented by a JSON list
* Message types shall be represented by a dictionary
* Byte types shall be represented by escaped unicode strings

# Usage
Given the protocol prototype below and the [GPB-Python Tool](@ref GPBBufferReadme)

~~~
message CPULoadingRequest { 
	enum RequestTypeT {
		STOP = 0;
		RUN = 1;
		REPORT = 2;
	}
	
	required RequestTypeT requestType = 1 [default = STOP];
	optional float level = 2;
}
~~~

We can use the GPB Buffers within python as follows:
~~~~~~~~~~~~~{.py}     
        message = CPULoadingRequest()

        message.requestType = CPULoadingRequest.RUN
        message.level = 50

        messageName, json = JsonConversion.gpb2json(message)
~~~~~~~~~~~~~
Which will convert the CPULoadingRequest into
+ messageName : (String) The name of the message ('CPULoadingRequest')
+ JSON serialization : {'requestType': 'RUN', 'level': 50.0}

~~~~~~~~~~~~~{.py}     
        message = JsonConversion.json2gpb(messageName, json)
~~~~~~~~~~~~~

The deserialization process is simular, where the messages name and json 
data are provided and the message class is returned.


