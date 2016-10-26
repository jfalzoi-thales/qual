#!/usr/bin/env bash

if [ $# == 2 ]; then
    echo "SUCCESS! $0 $@" >> /tmp/sematools.log
    exit 0
else
    echo "FAILURE! $0 $@" >> /tmp/sematools.log
    exit 1
fi