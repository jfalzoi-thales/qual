#!/bin/sh

if [ ! -e tklabs_utils/tzmq/ThalesZMQServer.py ] || [ ! -e simulator/gpio/gpioMgrSim.py ]; then
    echo "Please run this script from the 'src' directory of the project"
    exit 1
fi

export PYTHONPATH=`pwd`

python simulator/arinc429/arinc429DrvSim.py -e &
python simulator/arinc717/arinc717DrvSim.py &
python simulator/gpio/gpioMgrSim.py &
python simulator/pwrsupp/pwrSuppMonSim.py &
python simulator/sema/semaDrvSim.py &
python simulator/rtc/rtcDrvSim.py &

# Only start HDDS simulator if real HDDS is not installed
if [ ! -f /thales/host/appliances/HDDS ]; then
    python simulator/hdds/hddsSim.py &
fi

# Only start extern_Rs485 if there's at least one USB serial device
USBSERIAL=`ls /dev/ttyUSB* 2>/dev/null`
if [ -n "$USBSERIAL" ]; then
    (sleep 10; python simulator/Extern_Rs485/Extern_Rs485.py -m) &
fi
