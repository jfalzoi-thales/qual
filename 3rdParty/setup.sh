#!/bin/bash

echo This should install all required packages
echo

MAIN_WD=pwd

#------------------------------------------------------------------------
# Build:
#  Parallel Memory Bandwidth (PMBW)
# Notes:
#  This has to be done only once. An executable of this application
#   can be found: https://panthema.net/2013/pmbw/
#-------------------------------------------------------------------------
MEMBANDMODULE_WD="../../src/qual/modules/memorybandwidth/pmbw"

if [ -a $MEMBANDMODULE_WD]
then
    echo "PMBW tool already exists..."
else
    echo
    echo "Configuring..."

    cd pmbw
    PMBW_WD=pwd
    ./configure

    echo
    echo "Making..."
    make

    echo "Installing.."
    make install

    echo
    echo "Copying files to Module MemoryBandwidth..."
    cp "/usr/local/bin/pmbw" $MEMBANDMODULE_WD

    cd ..
    echo "------------------ DONE with PMBW!!! ------------------"
fi

#------------------------------- PMBW setup completed ---------------------------