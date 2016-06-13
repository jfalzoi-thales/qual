Memory Bandwidth Module
=======================
The memory bandwidth measurement is performed using the Parallel Memory Bandwidth (pmbw ) tool;  
a set of assembler routines to measure the parallel memory (cache and RAM) bandwidth of modern multicore machines.  
The current version of pmbw supports benchmarking 16-, 32-, 64-, 128-, or 256-bit memory transfers on x86_32-bit,  
x86_64-bit, and ARMv6 systems. It is available at http://freecode.com/projects/pmbw  

##### Memory Bandwidth Message Request:
  - enum RequestTypeT {STOP=0; RUN=1; REPORT=2}
  - required RequestTypeT requestType = 1 [default = STOP]
  
##### Memory Bandwidth Message Response:
  - required AppStateT state = 1;
  - required float memoryBandWidth = 2;