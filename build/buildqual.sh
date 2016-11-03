#!/bin/bash

UTILSDIR=~/tklabs-tklabs_utils
NMSDIR=~/tklabs-nms
QUALDIR=~/qual
MPSBUILDDIR=~/mps-builder

BUILD="QUAL"
TAG="NO"
NMS="NO"
BRANCH=""

# Display buildqual command usage
usage() {
    echo "Unrecognized parameter specified.  Accepted parameters are:
                -t|--tag    - builds RPMs with a new tag if BRANCH specified
                -b|--branch - builds images from specified branch
                -s|--sims   - builds only qual-sims image
                -n|--nms    - builds nms and tklabs_utils rpms from QUAL tree
                -a|--all    - builds both qual and qual-sims images"
    exit 1
}

# Handle tito tag and build for tklabs_utils from qual tree
titoutils() {
    echo "Building tklabs_utils RPMs from QUAL tree! ('-')"
    cd ${QUALDIR}/src/tklabs_utils
    if [ "$TAG" == "YES" ]; then tito tag; fi
    UTILSVERSION=`cat ${QUALDIR}/.tito/packages/tklabs_utils | cut -f 1 -d ' '`
    tito build --rpm --tag=tklabs_utils-${UTILSVERSION} --offline
}

# Handle tito tag and build for nms from qual tree
titonms() {
    echo "Building nms RPMs from QUAL tree! ( '-')"
    cd ${QUALDIR}/src/nms
    if [ "$TAG" == "YES" ]; then tito tag; fi
    NMSVERSION=`cat ${QUALDIR}/.tito/packages/nms | cut -f 1 -d ' '`
    tito build --rpm --tag=nms-${NMSVERSION} --offline
}

# Handle tito tag and build for qual
titoqual () {
    echo "Building qual RPMs! ('-' )"
    cd ${QUALDIR}/src
    tito init

    if [ "$TAG" == "YES" ]; then tito tag; fi

    VERSION=`cat ${QUALDIR}/.tito/packages/qual | cut -f 1 -d ' '`
    tito build --rpm --tag=qual-${VERSION} --offline
}

# Build qual pxe image
buildqual () {
    echo "(/*-*)/ Building qual images! \(*-*\)"
    cp ${QUALDIR}/build/mps-builder/config/pkgs-qual.inc.ks ${MPSBUILDDIR}/config/
    sudo docker run --net=host --rm=true -u root --privileged=true -v ${MPSBUILDDIR}:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7 /bin/bash "/mnt/workspace/dockerscripts/buildqual.script"
    cd ${MPSBUILDDIR}/bin/

    OLDQUALPXE=`ls -t1 livecd-mps-qual-*.tftpboot.tar.gz | head -1`
    TIMESTAMP=`echo ${OLDQUALPXE} | cut -f 4 -d '-'`
    NEWQUALPXE=livecd-mps-qual-${VERSION}-${TIMESTAMP}.tftpboot.tar.gz

    OLDQUALUSBDISK=`ls -t1 livecd-mps-qual-*.usbdisk.img.gz | head -1`
    TIMESTAMP=`echo ${OLDQUALUSBDISK} | cut -f 4 -d '-'`
    NEWQUALUSBDISK=livecd-mps-qual-${VERSION}-${TIMESTAMP}.usbdisk.img.gz

    OLDQUALUSBPART=`ls -t1 livecd-mps-qual-*.usbpart.img.gz | head -1`
    TIMESTAMP=`echo ${OLDQUALUSBPART} | cut -f 4 -d '-'`
    NEWQUALUSBPART=livecd-mps-qual-${VERSION}-${TIMESTAMP}.usbpart.img.gz

    sudo mv ${MPSBUILDDIR}/bin/${OLDQUALPXE} ${MPSBUILDDIR}/bin/${NEWQUALPXE}
    sudo mv ${MPSBUILDDIR}/bin/${OLDQUALUSBDISK} ${MPSBUILDDIR}/bin/${NEWQUALUSBDISK}
    sudo mv ${MPSBUILDDIR}/bin/${OLDQUALUSBPART} ${MPSBUILDDIR}/bin/${NEWQUALUSBPART}
}

# Build qual-sims pxe image
buildsims () {
    echo "(/~-~)/ Building qual-sims images! \(~-~\)"
    cp ${QUALDIR}/build/mps-builder/config/pkgs-qual-sims.inc.ks ${MPSBUILDDIR}/config/pkgs-qual.inc.ks
    sudo docker run --net=host --rm=true -u root --privileged=true -v ${MPSBUILDDIR}:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7 /bin/bash "/mnt/workspace/dockerscripts/buildqual.script"
    cd ${MPSBUILDDIR}/bin/

    OLDSIMSPXE=`ls -t1 livecd-mps-qual-*.tftpboot.tar.gz | head -1`
    TIMESTAMP=`echo ${OLDSIMSPXE} | cut -f 4 -d '-'`
    NEWSIMSPXE=livecd-mps-qual-sims-${VERSION}-${TIMESTAMP}.tftpboot.tar.gz

    OLDSIMSUSBDISK=`ls -t1 livecd-mps-qual-*.usbdisk.img.gz | head -1`
    TIMESTAMP=`echo ${OLDSIMSUSBDISK} | cut -f 4 -d '-'`
    NEWSIMSUSBDISK=livecd-mps-qual-sims-${VERSION}-${TIMESTAMP}.usbdisk.img.gz

    OLDSIMSUSBPART=`ls -t1 livecd-mps-qual-*.usbpart.img.gz | head -1`
    TIMESTAMP=`echo ${OLDSIMSUSBPART} | cut -f 4 -d '-'`
    NEWSIMSUSBPART=livecd-mps-qual-sims-${VERSION}-${TIMESTAMP}.usbpart.img.gz

    sudo mv ${MPSBUILDDIR}/bin/${OLDSIMSPXE} ${MPSBUILDDIR}/bin/${NEWSIMSPXE}
    sudo mv ${MPSBUILDDIR}/bin/${OLDSIMSUSBDISK} ${MPSBUILDDIR}/bin/${NEWSIMSUSBDISK}
    sudo mv ${MPSBUILDDIR}/bin/${OLDSIMSUSBPART} ${MPSBUILDDIR}/bin/${NEWSIMSUSBPART}
}

# Builds qual-ife guest vm image
buildife () {
    echo "(/'-')/ Building qual-guest images! \('-'\)"
    sudo docker run --net=host --rm=true -u root --privileged=true -v ${MPSBUILDDIR}:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7 /bin/bash "/mnt/workspace/dockerscripts/buildguest.script"
    cd ${MPSBUILDDIR}/bin/
    GUESTVMRPM=`ls -t1 mps-guest-vm-*.x86_64.rpm | head -1`
    sudo mv ${MPSBUILDDIR}/bin/mps-guest-vm-*.rpm ${MPSBUILDDIR}/repo/packages/x86_64/
    sudo createrepo --update ${MPSBUILDDIR}/repo/packages/
    sudo rm -f ${MPSBUILDDIR}/bin/*guest*
}


# Check for parameters: 
# if none,	    build only qual image
# if tag,	    build RPMs with a new tag
# if branch     build images from specified branch
# if sims,	    build only sims image
# if nms,       build nms and tklabs_utils rpms from Thales Github repo
# if all,	    build both
TEMP=`getopt -o tb:sna --long tag,branch:,sims,nms,all -n 'buildqual.sh' -- "$@" 2>/dev/null`
if [ "$?" != 0 ]; then usage; fi
eval set -- "$TEMP"

while true ; do
    case "$1" in
        -t|--tag)
            TAG="YES"
            shift;;
        -b|--branch)
            BRANCH="$2"
            shift 2;;
        -s|--sims)
            BUILD="SIMS"
            shift;;
        -n|--nms)
            NMS="YES"
            shift;;
        -a|--all)
            BUILD="ALL"
            shift;;
        --)
            shift; break;;
    esac
done

if [ "$#" != 0 ]; then usage; fi

if [ "$TAG" == "YES" -a -n "$BRANCH" ]; then
    echo "ERROR: BRANCH must be specified to use -t|--tag"
    usage
fi

set -e

# Build main qual RPMs and copy into repo
cd ${QUALDIR}/
echo "Please use your own Git credentials to log in. \(^^\) \(^^)/ (/^^)/"

if [ "$BRANCH" ]; then
    git fetch --tags origin "$BRANCH"
    git checkout "$BRANCH"
    git reset --hard FETCH_HEAD
fi

git clean -df
rm -rf /tmp/tito
tito init

if [ "$NMS" == "YES" ]; then
    titoutils
    titonms
fi

titoqual

if [ "$TAG" == "YES" ]; then
    git push --tags origin "$BRANCH"
fi

cp -r ${QUALDIR}/build/mps-builder/* ${MPSBUILDDIR}/

if [ "$NMS" == "YES" ]; then
    sudo rm -f ${MPSBUILDDIR}/repo/packages/x86_64/nms-*.rpm
    sudo rm -f ${MPSBUILDDIR}/repo/packages/x86_64/tklabs_utils-*.rpm
fi

sudo rm -f ${MPSBUILDDIR}/repo/packages/x86_64/qual-*.rpm
sudo mv /tmp/tito/x86_64/* ${MPSBUILDDIR}/repo/packages/x86_64/

# Build supplemental qual RPMs and copy into repo
cd ${QUALDIR}/thales
./build.sh
for file in /tmp/thales-rpms/*.rpm; do
    basepkg=`rpm -q --queryformat='%{NAME}' -p ${file}`
    sudo rm -f ${MPSBUILDDIR}/repo/packages/x86_64/${basepkg}-[0-9]*.rpm
done
sudo mv /tmp/thales-rpms/*.rpm ${MPSBUILDDIR}/repo/packages/x86_64/

# Build 3rdParty qual RPMs and copy into repo
cd ${QUALDIR}/3rdParty
./build.sh
for file in /tmp/3rdParty-rpms/*.rpm; do
    basepkg=`rpm -q --queryformat='%{NAME}' -p ${file}`
    sudo rm -f ${MPSBUILDDIR}/repo/packages/x86_64/${basepkg}-[0-9]*.rpm
done
sudo mv /tmp/3rdParty-rpms/*.rpm ${MPSBUILDDIR}/repo/packages/x86_64/

# Update the repo before we build the guest VM image
cd
sudo rm -f ${MPSBUILDDIR}/repo/packages/x86_64/mps-guest-vm-*.rpm
sudo createrepo --update ${MPSBUILDDIR}/repo/packages/

# Build guest-vm RPM and store in repo
buildife

case "$BUILD" in
    "QUAL") buildqual;;
    "SIMS") buildsims;;
     "ALL") buildqual; buildsims;;
esac

if [ "$BUILD" != "SIMS" ]; then
    echo "Built qual PXE image: $NEWQUALPXE"
    echo "Built qual USBDISK image: $NEWQUALUSBDISK"
    echo "Built qual USBPART image: $NEWQUALUSBPART"
fi

if [ "$BUILD" != "QUAL" ]; then
    echo "Built qual-sims PXE image: $NEWSIMSPXE"
    echo "Built qual-sims USBDISK image: $NEWSIMSUSBDISK"
    echo "Built qual-sims USBPART image: $NEWSIMSUSBPART"
fi

exit
