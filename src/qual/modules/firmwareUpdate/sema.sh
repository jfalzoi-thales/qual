#!/usr/bin/env bash

if [ $# == 2 ]; then
    echo "SUCCESS! $0 $@" >> /tmp/i350tools.log
    exit 0
else
    echo "FAILURE! $0 $@" >> /tmp/i350tools.log
    exit -1
fi