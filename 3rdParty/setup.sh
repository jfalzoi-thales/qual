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
echo "Copying files to $PMBW_WD..."
cp "/usr/local/bin/pmbw" "../../src/qual/modules/memorybandwidth"

cd ..

echo "------------------ DONE with PMBW!!! ------------------"

#------------------------------- PMBW setup completed ---------------------------