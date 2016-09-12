#!/bin/sh

# This script checks out mps-builder and sets everything up to build
# the base packages needed for the Qual build.
# The last thing it does is start a docker container to do the build;
# the user then types the command to actually run the build.
# This separation is so that the user can enter git credentials.

QUALDIR=~/qual
MPSBUILDDIR=~/mps-builder

set -e

if [ ! -e ${QUALDIR}/build/package.tags ]; then
    echo "Please check out QUAL repo into ~/qual before running this script"
    exit 1
fi

if [ ! -e ${MPSBUILDDIR}/build.sh ]; then
    cd ~/
    echo "Cloning mps-builder repo; enter credentials if necessary"
    git clone https://github.com/mapcollab/mps-builder.git
else
    echo "Cleaning mps-builder"
    cd ${MPSBUILDDIR}
    git clean -qdf
    git checkout -q -- .
fi

MPSBUILDTAG=`grep ^mps-builder ${QUALDIR}/build/package.tags | cut -f 2 -d ' ' -s`
echo "Checking out tag ${MPSBUILDTAG}"
cd ${MPSBUILDDIR}
git checkout -q --detach tags/${MPSBUILDTAG}

# Build docker container if not available
docker images | grep -q ^mps/mpsbuilder
if [ "$?" != 0 ]; then
    docker build -t mps/mpsbuilder:centos7 dockerfile/
fi

echo "Applying mps-builder changes for Qual"
cp -r ${QUALDIR}/build/mps-builder/* ${MPSBUILDDIR}/
cat ${MPSBUILDDIR}/config/package.tags.add >> ${MPSBUILDDIR}/config/package.tags

echo
echo "Entering docker for build; at root prompt below type:"
echo "   /mnt/workspace/build-qual-base.sh"
cd ${MPSBUILDDIR}
docker run -i --net="host" --rm=true -u root --privileged=true -v `pwd`:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7
