#!/bin/bash

QUALSRCDIR=/home/thales/qual/src
MPSBUILDDIR=/home/thales/mps-builder
BUILD="QUAL"
RPM="YES"

# Display buildqual command usage
usage() {
    echo "Unrecognized parameter specified.  Accepted parameters are:
                -n|--norpm 	- builds images without re-building RPMs
                -s|--sims	- builds only qual-sims image
                -a|--all 	- builds both qual and qual-sims images"
    exit 1
}

# Handle tito tag and build for qual
titoqual () {
    echo "Building qual RPMs! ('-' )"
    cd ${QUALSRCDIR}/
    tito init
    tito tag
    tito build --rpm --offline
}

# Build qual pxe image
buildqual () {
    echo "(/*-*)/ Building qual images! \(*-*\)"
    sudo cp ${QUALSRCDIR}/../build/pkgs-qual.inc.ks ${MPSBUILDDIR}/config/
    sudo docker run --net=host --rm=true -u root --privileged=true -v ${MPSBUILDDIR}:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7 /bin/bash "/mnt/workspace/dockerscripts/buildqual.script"
    cd ${MPSBUILDDIR}/bin/
    QUALPXE=`ls -t1 livecd-mps-qual-*.tftpboot.tar.gz | head -1`
    QUALUSBDISK=`ls -t1 livecd-mps-qual-*.usbdisk.img.gz | head -1`
    QUALUSBPART=`ls -t1 livecd-mps-qual-*.usbpart.img.gz | head -1`
}

# Build qual-sims pxe image
buildsims () {
    echo "(/~-~)/ Building qual-sims images! \(~-~\)"
    sudo cp ${QUALSRCDIR}/../build/pkgs-qual-sims.inc.ks ${MPSBUILDDIR}/config/pkgs-qual.inc.ks
    sudo docker run --net=host --rm=true -u root --privileged=true -v ${MPSBUILDDIR}:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7 /bin/bash "/mnt/workspace/dockerscripts/buildqual.script"
    cd ${MPSBUILDDIR}/bin/
    OLDSIMSPXE=`ls -t1 livecd-mps-qual-*.tftpboot.tar.gz | head -1`
    OLDSIMSUSBDISK=`ls -t1 livecd-mps-qual-*.usbdisk.img.gz | head -1`
    OLDSIMSUSBPART=`ls -t1 livecd-mps-qual-*.usbpart.img.gz | head -1`
    NEWSIMSPXE=${OLDSIMSPXE/livecd-mps-qual/livecd-mps-qual-sims}
    NEWSIMSUSBDISK=${OLDSIMSUSBDISK/livecd-mps-qual/livecd-mps-qual-sims}
    NEWSIMSUSBPART=${OLDSIMSUSBPART/livecd-mps-qual/livecd-mps-qual-sims}
    sudo mv ${MPSBUILDDIR}/bin/${OLDSIMSPXE} ${MPSBUILDDIR}/bin/${NEWSIMSPXE}
    sudo mv ${MPSBUILDDIR}/bin/${OLDSIMSUSBDISK} ${MPSBUILDDIR}/bin/${NEWSIMSUSBDISK}
    sudo mv ${MPSBUILDDIR}/bin/${OLDSIMSUSBPART} ${MPSBUILDDIR}/bin/${NEWSIMSUSBPART}
}

buildife () {
    echo "(/'-')/ Building qual-ife images! \('-'\)"
    sudo cp ${QUALSRCDIR}/../build/pkgs-guest.inc.ks ${MPSBUILDDIR}/config/
    sudo docker run --net=host --rm=true -u root --privileged=true -v ${MPSBUILDDIR}:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7 /bin/bash "/mnt/workspace/dockerscripts/buildguest.script"
    cd ${MPSBUILDDIR}/bin/
    GUESTVM=`ls -t1 livecd-mps-guest-*.vm.qcow2 | head -1`
    GUESTVMRPM=`ls -t1 mps-guest-vm-*.x86_64.rpm | head -1`
}


# Check for parameters: 
# if none,	build only qual image 
# if norpm,	build images without re-building RPMs
# if sims,	build only sims image 
# if all,	build both
TEMP=`getopt -o nsa --long norpm,sims,all -n 'buildqual.sh' -- "$@" 2>/dev/null`
if [ "$?" != 0 ]; then usage; fi
eval set -- "$TEMP"

while true ; do
    case "$1" in
        -n|--norpm)
            RPM="NO"
            shift;;
        -s|--sims)
            BUILD="SIMS"
            shift;;
        -a|--all)
            BUILD="ALL"
            shift;;
        --)
            shift; break;;
    esac
done

if [ "$@" != "" ]; then usage; fi

set -e

if [ $RPM == "YES" ]; then
    cd ${QUALSRCDIR}/
    echo "Please use your own Git credentials to log in. \(^^\) \(^^)/ (/^^)/"
    git fetch origin dev/QUAL
    git reset --hard FETCH_HEAD
    git clean -df
    rm -rf /tmp/tito
    titoqual
    git push origin dev/QUAL
    sudo rm -f ${MPSBUILDDIR}/repo/packages/x86_64/qual-*.rpm
    sudo rm -f ${MPSBUILDDIR}/repo/packages/x86_64/mps-guest-vm-*.rpm
    sudo rm -f ${MPSBUILDDIR}/bin/mps-guest-vm-*.rpm
    sudo mv /tmp/tito/x86_64/* ${MPSBUILDDIR}/repo/packages/x86_64/
    sudo createrepo --update ${MPSBUILDDIR}/repo/packages/
    # Build guest-vm RPM and store in repo
    buildife
    sudo rm -f ${MPSBUILDDIR}/bin/guest-vm*
    sudo cp ${MPSBUILDDIR}/bin/mps-guest-vm-*.rpm ${MPSBUILDDIR}/repo/packages/x86_64/
    sudo createrepo --update ${MPSBUILDDIR}/repo/packages/
fi

case $BUILD in
    "QUAL") buildqual;;
    "SIMS") buildsims;;
     "ALL") buildqual; buildsims;;
esac

echo "Built guest-vm image: $GUESTVM"
echo "Built guest-vm rpm: $GUESTVMRPM"

if [ $BUILD != "SIMS" ]; then 
    echo "Built qual PXE image: $QUALPXE"
    echo "Built qual USBDISK image: $QUALUSBDISK"
    echo "Built qual USBPART image: $QUALUSBPART"
fi

if [ $BUILD != "QUAL" ]; then 
    echo "Built qual-sims PXE image: $NEWSIMSPXE"
    echo "Built qual-sims USBDISK image: $NEWSIMSUSBDISK"
    echo "Built qual-sims USBPART image: $NEWSIMSUSBPART"
fi

exit
