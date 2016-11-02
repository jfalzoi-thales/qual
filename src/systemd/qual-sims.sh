#!/bin/bash

mkdir -p /thales/host/runtime/SEMADrv
gzip -c /thales/qual/src/simulator/sema/flash.txt > /thales/host/runtime/SEMADrv/flash

cd /thales/qual/src/
simulator/startsims.sh
