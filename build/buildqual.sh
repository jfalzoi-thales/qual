#!/bin/bash

if   [ $# -eq 0 ];  then BUILD="QUAL"
elif [ $1 == vm ];  then BUILD="VM"
elif [ $1 == all ]; then BUILD="ALL"
else
    echo "Unrecognized parameter specified.  Accepted parameters are:
    all - builds both qual and qual-vm images
     vm - builds only qual-vm image"
    exit
fi

QUALSRCDIR=/home/thales/qual/src
MPSBUILDDIR=/home/thales/mps-builder

titoqual () {
    cd ${QUALSRCDIR}/
    tito tag
    tito build --rpm --offline
}

titovm () {
    cd ${QUALSRCDIR}/simulator/
    tito tag
    tito build --rpm --offline
}

buildqual () {
    sudo cp ${QUALSRCDIR}/../build/qual-pkgs-psi.inc.ks ${MPSBUILDDIR}/config/pkgs-psi.inc.ks
    sudo docker run --net=host --rm=true -u root --privileged=true -v ${MPSBUILDDIR}:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7 /bin/bash "/mnt/workspace/build.script"
    cd ${MPSBUILDDIR}/bin/
    OLDQUAL=`ls -t1 livecd-mps-psi-*.gz | head -1`
    NEWQUAL=${OLDQUAL/livecd-mps-psi/livecd-mps-qual}
    sudo mv ${MPSBUILDDIR}/bin/${OLDQUAL} ${MPSBUILDDIR}/bin/${NEWQUAL}
}

buildvm () {
    sudo cp ${QUALSRCDIR}/../build/qual-vm-pkgs-psi.inc.ks ${MPSBUILDDIR}/config/pkgs-psi.inc.ks
    sudo docker run --net=host --rm=true -u root --privileged=true -v ${MPSBUILDDIR}:/mnt/workspace -v /dev:/dev -t mps/mpsbuilder:centos7 /bin/bash "/mnt/workspace/build.script"
    cd ${MPSBUILDDIR}/bin/
    OLDVM=`ls -t1 livecd-mps-psi-*.gz | head -1`
    NEWVM=${OLDVM/livecd-mps-psi/livecd-mps-qual-vm}
    sudo mv ${MPSBUILDDIR}/bin/${OLDVM} ${MPSBUILDDIR}/bin/${NEWVM}
}

set -e
cd ${QUALSRCDIR}/
git fetch origin dev/QUAL
git reset --hard FETCH_HEAD
git clean -df
rm -rf /tmp/tito
tito init
titoqual

if [ $BUILD != "QUAL" ]; then titovm; fi

sudo rm -f ${MPSBUILDDIR}/repo/packages/x86_64/qual-*.rpm
sudo mv /tmp/tito/x86_64/* ${MPSBUILDDIR}/repo/packages/x86_64/
sudo createrepo --update ${MPSBUILDDIR}/repo/packages/

case $BUILD in
    "QUAL") buildqual;;
      "VM") buildvm;;
     "ALL") buildqual; buildvm;;
esac

git push origin dev/QUAL

if [ $BUILD != "VM" ]; then 
    echo "Built QUAL image: $NEWQUAL"
fi

if [ $BUILD != "QUAL" ]; then 
    echo "Built QUAL-VM image: $NEWVM"
fi

exit
