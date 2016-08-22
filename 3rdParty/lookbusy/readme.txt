How to install lookbusy 1.4.  A tool used to generate synthetic CPU load among other functions:

1. Navigate to directory containing lookbusy-1.4-1.x86_64.rpm
2. Run 'sudo rpm -Uvh lookbusy-1.4-1.x86_64.rpm'
3. Grin at the simplicity of rpm installations :D

How to use lookbusy 1.4:

1. Run 'lookbusy -qc #' where # is the percentage of desired CPU load (-q means quiet mode and -c denotes load to use)

How to stop lookbusy 1.4:

1. Run 'pkill -9 lookbusy' (NOTE: This will end all instances of lookbusy on your machine.  If you wish to stop specific instances, please look into how to use the 'kill' command to end specific programs using their PID.)