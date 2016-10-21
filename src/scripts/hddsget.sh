#!/bin/bash
cd /thales/qual/src/
PYTHONPATH=`pwd` python qual/qte/hddsTest.py get $@
