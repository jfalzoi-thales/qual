#!/bin/sh

PIDS=`ps a | fgrep 'python simulator' | grep -v grep | cut -d ' ' -f 2`
if [ -z "$PIDS" ]; then
    echo "No simulators appear to be running"
    exit 0
fi

# Ugh, deal with situation where PID field doesn't have leading space
if [ `echo $PIDS | cut -c 1-3` == "pts" ]; then
    PIDS=`ps a | fgrep 'python simulator' | grep -v grep | cut -d ' ' -f 1`
fi

echo "Killing simulators on following pids:"
echo $PIDS
kill $PIDS
