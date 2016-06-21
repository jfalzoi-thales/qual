# System Monitoring Module

##### System Monitoring Request:
The System Monitoring Request Message is sent by the TE to request the MPS temperature, current, and voltage values obtained from internal sensors.  

  - message SystemMonitoringRequest {}  
    
##### System Monitoring Response:
The System Monitoring Response Message is sent by the MPS to report:  

  - Power Supply and Carrier Card sensor data 
  - Processor Module SEMA data
  - Network Switch temperature and port statistics
  
The MPS temperature, current, and voltage values are returned along with two strings uniquely identifying the device and the sensor within the device providing the data.  
The device name is defined in the [plugins] section of the MPS configuration file IAW the MPS Power Supply Monitor ICD.  
The sensor name is defined in the Power Supply Monitor Plugin ICD. Data from the SEMA device is returned in pairs of strings;  
one containing the logical name of the data and the other containing the data item value. One pair is sent for each data  
item defined in the MPS Smart Embedded Management Agent (SEMA) Driver Interface Control Document; section Board Information and Statistics Interface.  
The network switch temperature and port statistics are returned as one string containing the ascii coded temperature value and one string  
per Ethernet port containing the individual link state and traffic statistics for the individual port.  

  - message SensorValue {required string deviceName = 1; required string sensorName = 2; required string value = 3};
  - message SemaValue {required string itemName = 1; required string value = 2}
  - message SwitchData {required string temperture = 1; repeated string statistics = 2}
  - repeated SensorValue powerSupplyStatistics = 1;
  - repeated SemaValue semaStatistics = 2;
  - required SwitchData switchData = 3;