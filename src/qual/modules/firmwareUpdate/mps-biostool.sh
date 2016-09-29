#!/usr/bin/env bash

if [ $# == 2 ]; then
    if [ $1 == "set-active" ]; then
        if [ $2 == "primary" -o $2 == "secondary" ]; then
            echo "SUCCESS! $2 has been set! \o/"
            echo "SUCCESS - $0 $@" >> /tmp/biostool.log
            exit 0
        else
            echo "OH NO AN ERROR ;-;"
            echo "FAILURE - $0 $@" >> /tmp/biostool.log
            exit 1
        fi
    elif [ $1 == "program-from" ]; then
        if [ -f $2 ]; then
            echo "Successfully programmed BIOS from $2"
            echo "SUCCESS - $0 $@" >> /tmp/biostool.log
            exit 0
        else
            echo "OH NO AN ERROR (/-\)"
            echo "FAILURE - $0 $@" >> /tmp/biostool.log
            exit 1
        fi
    elif [ $1 == "set-mac" ]; then
        echo "Successfully programmed MAC Address: $2"
        echo "SUCCESS - $0 $@" >> /tmp/biostool.log
        exit 0
    fi
fi

echo "OH NO AN ERROR T-T"
echo "FAILURE - $0 $@" >> /tmp/biostool.log
exit 1
