#!/bin/sh

if [ "$#" -lt 3 ]; then
    echo "ERROR ERROR ERROR"
    exit 1
fi

if [ "$3" == "-k" ] && [ "$#" -eq 5 ]; then
    echo "some pin disabled"
    exit 0    
fi

if [ "$3" == "-a" ] && [ "$#" -eq 6 ]; then
    echo "some program succeeded"
    sleep 1
    exit 0
fi

echo "ERROR ERROR ERROR"
exit 1

