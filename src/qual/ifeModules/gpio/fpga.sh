#!/bin/bash



if [ "$#" -eq 1 ]; then
    if [ -e /tmp/fpga ]; then
        cat /tmp/fpga
    else
        echo "0x00"
    fi

    exit 0
elif [ "$#" -eq 2 ]; then
    SIXTH=$(( $2 & 0x20 ))

    if [ "$SIXTH" -gt 0 ]; then
        HEX=$(( $2 | 0xE0 ))
    else
        HEX=$(( $2 & ~0xE0 ))
    fi

    echo "$(printf 0x%x $HEX)" > /tmp/fpga
    exit 0
fi

# No output on error
exit 1
