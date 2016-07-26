#!/bin/sh

# This script goes into each subdirectory containing a spec file and
# builds RPMs from those spec files.  Built RPMs are placed in /tmp/thales-rpms .

if [ ! -e build.sh ] || [ ! -d ../3rdParty ]; then
    echo "Please run this from the thales directory"
    exit 1
fi

RPMDIR=/tmp/thales-rpms
rm -rf $RPMDIR
mkdir $RPMDIR

set -e

for DIRENT in *; do
    if [ -d "$DIRENT" ]; then
        cd $DIRENT
        SPEC=`ls -1 *.spec 2>/dev/null | head -1`
        if [ -n "$SPEC" ]; then
            echo "Building $SPEC in $DIRENT"
            rm -rf ~/rpmbuild
            rpmbuild --quiet --build-in-place -bb $SPEC
            if [ $? = 0 ]; then
                mv ~/rpmbuild/RPMS/*/*.rpm $RPMDIR
            else
                echo "rpmbuild failed!"
            fi
            rm -rf ~/rpmbuild debugfiles.list debuglinks.list debugsources.list elfbins.list
        fi
        cd ..
    fi
done
echo
echo "Built RPMs in $RPMDIR:"
cd $RPMDIR
ls -1 | fgrep -v debuginfo
