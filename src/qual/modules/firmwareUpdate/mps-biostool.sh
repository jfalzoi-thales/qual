#!/usr/bin/env bash

if [ $# == 2 ]; then
    if [ $1 == "set-active" ]; then
        if [ $2 == "primary" -o $2 == "secondary" ]; then
            echo "SUCCESS! $2 has been set! \o/"
            exit 0
        else
            echo "OH NO AN ERROR ;-;"
            exit 1
        fi
    elif [ $1 == "program-from" ]; then
        if [ -f $2 ]; then
            echo "Successfully programmed BIOS from $2"
            exit 0
        else
            echo "OH NO AN ERROR (/-\)"
            exit 1
        fi
    fi
fi

echo "OH NO AN ERROR T-T"
exit 1
