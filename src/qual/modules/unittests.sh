#!/bin/sh

if [ ! -d qual/modules ]; then
    echo "Please run this from the src directory"
    exit 1
fi

export PYTHONPATH=`pwd`
python -m unittest discover -s qual/modules -p "unitTest_*.py" 2>&1 | tee /tmp/unittests.txt
