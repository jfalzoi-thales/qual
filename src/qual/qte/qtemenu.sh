#!/usr/bin/env bash
if [ ! /thales/host/appliances ]
then
    mkdir -p /thales/host/appliances
fi

cd /thales/qual/src/

PYTHONPATH=`pwd` python qual/qte/qteMenu.py