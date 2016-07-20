#!/bin/bash

BUILD="QUAL"
RPM="YES"

# Check for parameters, 
# if none, 	build only qual image 
# if norpm, 	build images without re-building RPMs
# if vm,   	build only vm image 
# if all,  	build both
TEMP=`getopt -o nva --long norpm,vm,all -n 'buildqual.sh' -- "$@"`
eval set -- "$TEMP"

while true ; do
    case "$1" in
	-n|--norpm)
	    RPM="NO"
	    shift;;
	-v|--vm)
	    BUILD="VM"
	    shift;;
	-a|--all)
	    BUILD="ALL"
	    shift;;
	--)
	    shift; break;;
	*)
    	    echo "Unrecognized parameter specified.  Accepted parameters are:
    		-n|--norpm 	- builds images without re-building RPMs
     		-v|--vm 	- builds only qual-vm image
		-a|--all 	- builds both qual and qual-vm images"
    	    exit 1;;
    esac
done

QUALSRCDIR=/home/thales/qual/src
MPSBUILDDIR=/home/thales/mps-builder

# Handle tito tag and build for qual
titoqual () {
    echo "Building qual RPM! ('-' )"
    cd ${QUALSRCDIR}/
    tito tag
    tito build --rpm --offline
}

# Handle tito tag and build for qual-vm
titovm () {
    echo "Building qual-vm RPM! (._. )"
    cd ${QUALSRCDIR}/simulator/
    tito tag
    tito build --rpm --offline
}

# Build qual pxe image
buildqual () {
    echo "(/*-*)/ Building qual images! \(*-*\)
    sudo cp ${QUALSRCDIR}/../build/pkgs-qual.inc.ks ${MPSBUILDDIR}/config/
    sudo docker run --net=host --rm=true -u root --privileged=true -v ${MPSBUILDDIR}:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7 /bin/bash "/mnt/workspace/build.script"
    cd ${MPSBUILDDIR}/bin/
    QUALPXE=`ls -t1 livecd-mps-qual-*.tftpboot.tar.gz | head -1`
    QUALUSBDISK=`ls -t1 livecd-mps-qual-*.usbdisk.img.gz | head -1`
    QUALUSBPART=`ls -t1 livecd-mps-qual-*.usbpart.img.gz | head -1`
}

# Build qual-vm pxe image
buildvm () {
    echo "(/~-~)/ Building qual-vm images! \(~-~\)
    sudo cp ${QUALSRCDIR}/../build/pkgs-qual-vm.inc.ks ${MPSBUILDDIR}/config/pkgs-qual.inc.ks
    sudo docker run --net=host --rm=true -u root --privileged=true -v ${MPSBUILDDIR}:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7 /bin/bash "/mnt/workspace/build.script"
    cd ${MPSBUILDDIR}/bin/
    OLDVMPXE=`ls -t1 livecd-mps-qual-*.tftpboot.tar.gz | head -1`
    OLDVMUSBDISK=`ls -t1 livecd-mps-qual-*.usbdisk.img.gz | head -1`
    OLDVMUSBPART=`ls -t1 livecd-mps-qual-*.usbpart.img.gz | head -1`
    NEWVMPXE=${OLDVMPXE/livecd-mps-qual/livecd-mps-qual-vm}
    NEWVMUSBDISK=${OLDVMUSBDISK/livecd-mps-qual/livecd-mps-qual-vm}
    NEWVMUSBPART=${OLDVMUSBPART/livecd-mps-qual/livecd-mps-qual-vm}
    sudo mv ${MPSBUILDDIR}/bin/${OLDVMPXE} ${MPSBUILDDIR}/bin/${NEWVMPXE}
    sudo mv ${MPSBUILDDIR}/bin/${OLDVMUSBDISK} ${MPSBUILDDIR}/bin/${NEWVMUSBDISK}
    sudo mv ${MPSBUILDDIR}/bin/${OLDVMUSBPART} ${MPSBUILDDIR}/bin/${NEWVMUSBPART}
}

set -e

if [ $RPM == "YES" ]; then
    cd ${QUALSRCDIR}/
    echo "Please use your own Git credentials to log in. \(^^\) \(^^)/ (/^^)/"
    git fetch origin dev/QUAL
    git reset --hard FETCH_HEAD
    git clean -df
    rm -rf /tmp/tito
    tito init
    titoqual

    if [ $BUILD != "QUAL" ]; then titovm; fi

    git push origin dev/QUAL
fi

sudo rm -f ${MPSBUILDDIR}/repo/packages/x86_64/qual-*.rpm
sudo mv /tmp/tito/x86_64/* ${MPSBUILDDIR}/repo/packages/x86_64/
sudo createrepo --update ${MPSBUILDDIR}/repo/packages/

case $BUILD in
    "QUAL") buildqual;;
      "VM") buildvm;;
     "ALL") buildqual; buildvm;;
esac

if [ $BUILD != "VM" ]; then 
    echo "Built QUAL PXE image: $QUALPXE"
    echo "Built QUAL USBDISK image: $QUALUSBDISK"
    echo "Built QUAL USBPART image: $QUALUSBPART"
fi

if [ $BUILD != "QUAL" ]; then 
    echo "Built QUAL-VM PXE image: $NEWVMPXE"
    echo "Built QUAL-VM USBDISK image: $NEWVMUSBDISK"
    echo "Built QUAL-VM USBPART image: $NEWVMUSBPART"
fi

exit
