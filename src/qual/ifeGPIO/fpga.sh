#!/bin/sh

if [ "$#" -eq 1 ]; then
    if [ -e /tmp/fpga ]; then
        cat /tmp/fpga
    else
        echo "0x00"
    fi
    exit 0
elif [ "$#" -eq 2 ]; then
    echo "$2" > /tmp/fpga
    exit 0
fi

# No output on error
exit 1
