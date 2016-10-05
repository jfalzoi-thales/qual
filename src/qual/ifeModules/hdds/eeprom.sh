#!/usr/bin/env bash

EEPROM="/tmp/EEPROM"

if [ ! -d "$EEPROM" ]; then
    mkdir -p "$EEPROM"
fi

if [ $# == 1 ]; then
    cat "$EEPROM/$1"
    exit 0
elif [ $# == 2 ]; then
    echo "$2" > "$EEPROM/$1"
    exit 0
else
    echo "INCORRECT FUNCTION CALL"
    exit 1
fi
