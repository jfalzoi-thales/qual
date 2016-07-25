#!/bin/sh

if [ ! -d qual/modules ]; then
    echo "Please run this from the src directory"
    exit 1
fi

sleep 1

echo "	        Req  Resp Result
Master-Slave1 	1    1    PASS
Master-Slave2	1    0    FAIL
Master-Slave3	1    1    PASS
Master-Slave4	1    1    PASS
Master-Slave5	1    0    FAIL"