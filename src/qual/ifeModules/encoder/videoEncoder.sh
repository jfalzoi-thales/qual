#!/usr/bin/env bash

if [[ $1 = "status" ]]
then
    if [ -e /tmp/videoEncoder.tmp ]
    then
        echo "Runnning"
    else
        echo "Stopped"
    fi
elif [[ $1 = "start" ]]
then
    echo "videoEncoder" > /tmp/videoEncoder.tmp
elif [[ $1 = "stop" ]]
then
    rm /tmp/videoEncoder.tmp
else
    echo
    echo "Ivalid Parameter."
    echo
fi