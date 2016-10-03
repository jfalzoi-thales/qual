#!/bin/sh

if [ ! -e /usr/bin/demo_binaryio ]; then
    echo "IFE tools do not appear to be installed"
    exit 1
fi

if [ ! -e /thales/qual/src/qual/ifeModules/encoder/videoEncoder.sh ]; then
    echo "Qual software does not appear to be installed"
    exit 1
fi

if [ -e /usr/bin-disabled/demo_binaryio ]; then
    echo "IFE simulator tools appear to already be installed"
    exit 1
fi

mkdir -p /usr/bin-disabled
cd /usr/bin
mv demo_binaryio demo_serial485 tempsensor voltsensor fpga pavaTest.sh videoEncoder.sh /usr/bin-disabled/
cd /thales/qual/src/qual/ifeModules
install -m755 arinc485/demo_serial485.sh /usr/bin/demo_serial485
install -m755 encoder/videoEncoder.sh /usr/bin/videoEncoder.sh
install -m755 hdds/tempsensor.sh /usr/bin/tempsensor
install -m755 hdds/voltsensor.sh /usr/bin/voltsensor
install -m755 analogAudio/pavaTest.sh /usr/bin/
install -m755 gpio/demo_binaryio.sh /usr/bin/demo_binaryio
install -m755 gpio/fpga.sh /usr/bin/fpga
