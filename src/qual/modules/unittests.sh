#!/bin/sh

ETHPATH=qual/modules/ethernet

if [ ! -d qual/modules ]; then
    echo "Please run this from the src directory"
    exit 1
fi

if [ -f ${ETHPATH}/unitTest_ethernet.py.bak ]; then
    mv -f ${ETHPATH}/unitTest_ethernet.py.bak ${ETHPATH}/unitTest_ethernet.py
fi

TEMP=`getopt -o i: --long iperf: -n 'unittests.sh' -- "$@"`
eval set -- "$TEMP"

while true ; do
    case "$1" in
        -i|--iperf) 
            IPADDR="$2"
            sed -i.bak 's/10.10.42.231/'"$IPADDR"'/g' ${ETHPATH}/unitTest_ethernet.py
            shift 2;;
        --)
            shift; break;;
        *)
            echo "Incorrect parameter!"; exit 1;;
    esac
done

export PYTHONPATH=`pwd`
python -m unittest discover -s qual/modules -p "unitTest_*.py" 2>&1 | tee /tmp/unittests.txt