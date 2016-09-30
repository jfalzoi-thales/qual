#!/bin/bash

# Mount tsp-download partition if present
TSPDL_DEV=/dev/mapper/unprotected_vg-swdownload
TSPDL_MOUNT=/tsp-download
mount | fgrep -q $TSPDL_MOUNT
if [ "$?" != 0 -a -e $TSPDL_DEV ]; then
    mount $TSPDL_DEV $TSPDL_MOUNT
    if [ "$?" == 0 ]; then
        echo "TSP download directory mounted on $TSPDL_MOUNT"
    else
        echo "Failed to mount TSP download directory from $TSPDL_DEV"
    fi
fi

# Start up Qual
echo "Qual package version is: `rpm -q --queryformat='%{VERSION}' qual`"
cd /thales/qual/src/
PYTHONPATH=`pwd` python qual/qta/qta.py
