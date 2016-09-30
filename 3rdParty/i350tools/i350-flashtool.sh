#!/bin/bash

PCIADDR=`lspci | grep -m 1 I350 | awk '{print $1}'`
FILE=$1

if [ -z "$PCIADDR" ]; then
    echo "I350 device not detected"
    exit 1
fi

if [ ! -f "$FILE" ] ; then
    echo "Firmware file $FILE not found"
    exit 1
fi

echo "PCI ADDR = $PCIADDR"
echo "File     = $FILE"

flashrom_i350 -p nicintel_spi:pci="$PCIADDR" -w $FILE
