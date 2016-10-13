#!/bin/bash

. $SCRIPTS/functions.inc


PKG=centos7-kernel-builder

KERNEL_BRANCH=master
KERNEL_TAG=`package_tag $PKG $TESTBLD`

build_failed() {
	# Restore rpmbuild directory
	rm -f $RPMBUILD_PATH
	[ -d $RPMBUILD_PATH.orig ] && mv $RPMBUILD_PATH.orig $RPMBUILD_PATH

	# Return to top directory
	cd $TOPDIR
	exit 1
}

echo "Preparing for kernel build..."

RPMBUILD_PATH=`echo ~/rpmbuild`

# Use local rpmbuild directory
[ -d $RPMBUILD_PATH ] && mv -f $RPMBUILD_PATH $RPMBUILD_PATH.orig
mkdir -p $TOPDIR/tmp/rpmbuild
ln -sf $TOPDIR/tmp/rpmbuild $RPMBUILD_PATH

# Remove old rpms
rm -f $RPMBUILD_PATH/RPMS/x86_64/*.rpm

# Create repository path
mkdir -p $PATH_KERNEL_REPO/x86_64/

# Clone kernel builder sources
if [ ! -d $MPSSRC/kernel ]; then
	echo "Clonning kernel to $MPSSRC/kernel..."
	git clone $GIT_URL/$PKG.git -b $KERNEL_BRANCH $MPSSRC/kernel >/dev/null
elif [ -d $MPSSRC/kernel/.git ] && [ "$OFFLINE" != "1" ]; then
	echo "Updating kernel..."
	pushd $MPSSRC/kernel && git checkout $KERNEL_BRANCH && git pull && popd >/dev/null 2>&1
fi

# If this is stable build update to the tag
if [ $TESTBLD -eq 0 ] && [ "$KERNEL_TAG" != "" ]; then
	echo "Getting tag $KERNEL_TAG"
	pushd $MPSSRC/kernel && git checkout $KERNEL_TAG && popd >/dev/null 2>&1
fi

# Install dependencies
if [ ! -f $MPSSRC/kernel.deps ]; then
	echo "Installing Build dependencies..."
	yum-builddep -y $MPSSRC/kernel/rpm/kernel.spec >/dev/null || build_failed
	touch $MPSTMP/kernel.deps
fi

# Clone centos-kernel to work around problem with build script and remote repositories
cd $MPSSRC/kernel
echo "Cloning kernel sources to $MPSSRC/kernel/centos7-kernel..."
git clone $GIT_URL/centos7-kernel.git -b $KERNEL_BRANCH > /dev/null

# Build kernel
echo "Building kernel..."
cd $MPSSRC/kernel
./build-kernel.sh $KERNEL_TAG >$MPSTMP/kernel.log 2>&1 || { cat $MPSTMP/kernel.log; build_failed; }

echo "Updating repository $PATH_KERNEL_REPO..."

# Copy kernel RPMs from rpmbuild to kernel repo
mv -f $RPMBUILD_PATH/RPMS/x86_64/*.rpm $PATH_KERNEL_REPO/x86_64/

# Create repository
createrepo $PATH_KERNEL_REPO/

# Return to top directory
cd $TOPDIR

# Restore rpmbuild directory
rm -f $RPMBUILD_PATH
[ -d $RPMBUILD_PATH.orig ] && mv $RPMBUILD_PATH.orig $RPMBUILD_PATH

echo "Kernel done"

exit 0
