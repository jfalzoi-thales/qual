#!/bin/sh

if [ "$#" -eq 1 ]; then
    if [ -e /tmp/fpga.$1 ]; then
        cat /tmp/fpga.$1
    else
        echo "0x00"
    fi
    exit 0
elif [ "$#" -eq 2 ]; then
    echo "$2" > /tmp/fpga.$1
    exit 0
fi

# No output on error
exit 1
