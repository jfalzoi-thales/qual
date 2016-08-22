#!/bin/sh

if [ "$#" -lt 3 ]; then
    echo "ERROR ERROR ERROR"
    exit 1
fi

if [ "$3" == "-k" ] && [ "$#" -eq 5 ]; then
    echo "$2 $4 disabled"
    exit 0    
fi

if [ "$3" == "-a" ] && [ "$#" -eq 6 ]; then
    sleep 1
    echo "$2 program succeeded"
    exit 0
fi

if [ "$2" == "loopback" ] && [ "$#" -eq 6 ]; then
    sleep 2
    echo "Loopback PA $4 to VA $6 succeeded"
    exit 0
fi

echo "ERROR ERROR ERROR"
exit 1
