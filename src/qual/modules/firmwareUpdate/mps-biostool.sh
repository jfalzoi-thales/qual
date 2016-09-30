#!/usr/bin/env bash

if [ ! -f /tmp/currentbank ]; then
    echo "0" > /tmp/currentbank
fi

if [ ! -f /tmp/primarymac ]; then
    echo "00:04:00:00:00:00" > /tmp/primarymac
fi

if [ ! -f /tmp/secondarymac ]; then
    echo "00:04:00:00:00:00" > /tmp/secondarymac
fi

if [ $# == 2 ]; then
    if [ $1 == "set-active" ]; then
        echo $2 > /tmp/currentbank
        echo "SUCCESS! $2 BIOS bank has been set! \o/"
        echo "SUCCESS - $0 $@" >> /tmp/biostool.log
        exit 0
    elif [ $1 == "program-from" ]; then
        echo "Successfully programmed BIOS from $2"
        echo "SUCCESS - $0 $@" >> /tmp/biostool.log
        exit 0
    elif [ $1 == "set-mac" ]; then
        if [ `cat /tmp/currentbank` == "0" ]; then
            echo $2 > /tmp/primarymac
            echo "Programming Primary BIOS MAC to $2"
        elif [ `cat /tmp/currentbank` == "1" ]; then
            echo $2 > /tmp/secondarymac
            echo "Programming Secondary BIOS MAC to $2"
        fi

        echo "SUCCESS - $0 $@" >> /tmp/biostool.log
        exit 0
    fi
elif [ $# == 1 ]; then
    if [ $1 == "get-active" ]; then
        cat /tmp/currentbank
        echo "SUCCESS - $0 $@" >> /tmp/biostool.log
        exit 0
    elif [ $1 == "get-mac" ]; then
        if [ `cat /tmp/currentbank` == 0 ]; then
            cat /tmp/primarymac
        elif [ `cat /tmp/currentbank` == 1 ]; then
            cat /tmp/secondarymac
        fi

        echo "SUCCESS - $0 $@" >> /tmp/biostool.log
        exit 0
    fi
fi

echo "OH NO AN ERROR T-T"
echo "FAILURE - $0 $@" >> /tmp/biostool.log
exit 1
