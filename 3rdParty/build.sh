#!/bin/sh

# This script goes into each subdirectory containing a spec file and
# builds RPMs from those spec files.  Built RPMs are placed in /tmp/thales-rpms .

if [ ! -e build.sh ] || [ ! -d ../thales ]; then
    echo "Please run this from the 3rdParty directory"
    exit 1
fi

RPMDIR=/tmp/3rdParty-rpms
rm -rf $RPMDIR
mkdir $RPMDIR

# Only directory we care about is lookbusy (see readme.txt)
# We have the completed RPMs checked in, so just use those.
cp lookbusy/lookbusy-*.rpm $RPMDIR

echo
echo "Built RPMs in $RPMDIR:"
cd $RPMDIR
ls -1 | fgrep -v debuginfo
