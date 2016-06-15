SSD Module
==========
The purpose of the SSD Utilization Application is to exercise the SSD RAID.  
The SSD Test deletes all existing RAID configurations prior to drive preparation operations, configures the four (4) internal  
SSDs in a RAID-0 configuration during test initialization, creates a non-bootable partition after RAID volume preparation,  
and create a ext4 filesystem on the RAID partition after creation of the partition.
The SSD Utilization function consists of invoking the FIO test program and reporting the results.  

##### SSD Request Message
  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2}
  - required RequestTypeT requestType = 1 [default = STOP];

##### SSD Response Message
  - enum AppStateT {STOPPED=0; RUNNING=1}
  - required AppStateT state = 1;