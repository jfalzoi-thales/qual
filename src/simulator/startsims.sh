#!/bin/sh

if [ ! -e common/tzmq/ThalesZMQServer.py ] || [ ! -e simulator/gpio/gpioMgrSim.py ]; then
    echo "Please run this script from the 'src' directory of the project"
    exit 1
fi

export PYTHONPATH=`pwd`

python simulator/arinc429/arinc429DrvSim.py -e &
python simulator/arinc717/arinc717DrvSim.py &
python simulator/gpio/gpioMgrSim.py &
python simulator/pwrsupp/pwrSuppMonSim.py &
python simulator/sema/semaDrvSim.py &
python simulator/Extern_Rs485/Extern_Rs485.py -m &
