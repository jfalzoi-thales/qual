#!/usr/bin/env bash

if [ $# == 2 ]; then
    if [ $2 == "-mac_dump" ]; then
        cat /tmp/i350mac_"${1: -1}"
        echo "SUCCESS! $0 $@" >> /tmp/i350tools.log
        exit 0
    fi
elif [ $# == 3 ]; then
    if [ $2 == "-a" ]; then
        cat $3 > /tmp/i350mac_"${1: -1}"
        echo "SUCCESS! $0 $@" >> /tmp/i350tools.log
        exit 0
    fi
fi

echo "FAILURE! $0 $@" >> /tmp/i350tools.log
exit 1
