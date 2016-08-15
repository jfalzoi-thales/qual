#!/bin/bash
echo "Qual package version is: `rpm -q --queryformat='%{VERSION}' qual`"
cd /thales/qual/src/
PYTHONPATH=`pwd` python qual/qta/qta.py
