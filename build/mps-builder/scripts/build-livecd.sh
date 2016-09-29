#!/bin/sh

. $SCRIPTS/functions.inc

TARGET=$1
SRCISO=$2

# targets:
# mps-all        (mps-map, mps-psi, mps-guest, mps-devel)
# mps-map        (MPS MAP   ISO+USB)
# mps-psi        (MPS PSI   PXE)
# mps-atp        (MPS ATP   ISO)
# mps-qual       (MPS QUAL  ISO+PXE)
# mps-devel      (MPS devel ISO+USB)
# mps-guest      (MPS guest ISO+qcow2+rpm)

[ -z "$TARGET" ] && TARGET="mps-all"
[ -n "$SRCISO" -a "$TARGET" = "mps-all" ] && { echo "You cannot provide srciso name for mps-all target!"; exit 1; }
[ -z "$BUILD_VER" ] && BUILD_VER="`date +%Y%m%d%H%M`-unkn"

echo
echo "Starting $0 with params:"
echo "TARGET=$TARGET"
echo "SRCISO=$SRCISO"
echo "BUILD_VER=$BUILD_VER"

# Find the recently created livecd iso image (or echo the pre-created image name of second argument)
iso_image_name() {
	[ -z "$SRCISO" ] && echo livecd-${1}-${BUILD_VER}.iso || echo $SRCISO
}


# Create ISO image
make_iso() {
	name=$1
	config=$2
	fslabel="${config%%.ks}-${BUILD_VER}"
	export IMAGE_TYPE="livecd"
	export IMAGE_TARGET="${config%%.ks}"
	echo "Creating a bootable ISO livecd image..."
	echo "PWD=$PWD"
	echo "IMAGE_TYPE=$IMAGE_TYPE"
	echo "IMAGE_TARGET=$IMAGE_TARGET"

	livecd-creator --debug --cache="$(realpath $MPSCACHE)" --title="$name" --fslabel="$fslabel" --product=MPS --config=$TOPDIR/config/$config -t $MPSTMP || exit 1
	mv "${fslabel}.iso" "`iso_image_name ${config%%.ks}`"
}

# Generate VM image
make_vm() {
	size=8G
	iso="$1"
	raw=${iso/.iso/.raw}
	img=${iso/.iso/.vm.qcow2}

	echo "Creating a VM image"
	echo "  Creating empty image of ${size}... (qemu-img)"
	qemu-img create -f raw $raw $size
	mke2fs $raw -F

	vmdev=`losetup --find --show $raw`
	echo "  Installing iso to image via $vmdev... (livecd-iso-to-disk)"
	livecd-iso-to-disk $iso $vmdev || exit 1
	sync
	losetup -d $vmdev

	echo "  Converting raw image to qcow2... (qemu-img)"
	qemu-img convert -f raw -O qcow2 $raw $img
	sync
	rm -f $raw
	echo "  Done! VM image ready at $MPSBIN/$img"
}

# Create an RPM with guest vm
make_vm_rpm() {
	iso="$1"
	img=${iso/.iso/.vm.qcow2}
	version=`echo $iso | cut -d "-" -f 4-4 | cut -d "." -f 1-1`

	# Create a rpmbuild directories
	RPMBUILD_PATH=`echo ~/rpmbuild`
	mkdir -p $RPMBUILD_PATH/BUILD
	mkdir -p $RPMBUILD_PATH/BUILDROOT
	mkdir -p $RPMBUILD_PATH/RPMS
	mkdir -p $RPMBUILD_PATH/SOURCES
	mkdir -p $RPMBUILD_PATH/SPECS
	mkdir -p $RPMBUILD_PATH/SRPMS

	echo "  Creating RPM... (rpmbuild)"

	# Copy VM image and spec
	cp -af $img $RPMBUILD_PATH/SOURCES/
	cp -af $TOPDIR/config/guest-vm.spec $RPMBUILD_PATH/SPECS/
	sed -i "s/RPM_VERSION/$version/g" $RPMBUILD_PATH/SPECS/guest-vm.spec

	# Build rpm
	rpmbuild -bb $RPMBUILD_PATH/SPECS/guest-vm.spec > /dev/null
	mv -f $RPMBUILD_PATH/RPMS/x86_64/mps-guest-vm-$version*.rpm $MPSBIN/
	echo "  Done! VM RPM ready at $MPSBIN/mps-guest-vm-$version-1.x86_64.rpm"
}

USB_LIVE_PARTITION_SIZE=1800   # target livecd partition size in MiB

# Generate USB image (BIOS-only bootable, MBR partitions, optional persistent /home partition)
make_usb() {
	iso="$1"
	disk_img=${iso/.iso/.usbdisk.img}
	part_img=${iso/.iso/.usbpart.img}
	size=$((USB_LIVE_PARTITION_SIZE*1024*1024/512))

	echo "Creating a bootable (BIOS) USB image"
	echo "  Creating empty image of $USB_LIVE_PARTITION_SIZE MiB... (dd)"
	dd if=/dev/zero of=$disk_img bs=512 count=$((size + 2048)) # bs=512: image must be aligned to 512B sector size; +2048=MBR overhead
	sync
	dev=$(losetup --find --show "$disk_img")
	echo "  Creating partitions & FS... (parted, mkfs.vfat)"
	/sbin/parted --script $dev mklabel msdos
	/sbin/parted --script $dev u s mkpart primary fat32 2048 $((2048+size-1)) set 1 boot on
	/sbin/udevadm settle
	if [ -f /usr/lib/syslinux/mbr.bin ]; then
		cat /usr/lib/syslinux/mbr.bin > $dev
	elif [ -f /usr/share/syslinux/mbr.bin ]; then
		cat /usr/share/syslinux/mbr.bin > $dev
	else
		echo "Could not find mbr.bin (have you installed syslinux?)"
		exit 1
	fi
	sleep 5
	sync
	# recreate the device to make sure partition table is refreshed
	losetup -v -d $dev
	dev=$(losetup --find --show -P "$disk_img") # note the -P option which forces partitions to be read and /dev/loop0p1 to be created
	part=${dev}p1
	mkfs.vfat -n MPS_LIVEUSB ${part}
	echo "  Converting iso to live image via ${dev}p1... (livecd-iso-to-disk)"
	livecd-iso-to-disk --label MPS_LIVEUSB "$iso" "${part}" || exit 1
	sync
	echo "  Compressing updateable USB live partition image... (gz)"
	dd if=${part} bs=1M | gzip -1 -c > ${part_img}.gz
	losetup -d $dev
	echo "  Compressing fresh-install USB disk image... (gz)"
	gzip -f -1 ${disk_img} # xz produces slightly smaller file (<1%), but takes 5-10x more time to compress. gzip is sufficient.
	echo "  Done! Full-disk image ready at $MPSBIN/${disk_img}.gz"
	echo "        Partition image ready at $MPSBIN/${part_img}.gz"
	echo "  1. Fresh install: (!!THIS WILL WIPE WHOLE USB DRIVE!!)"
	echo "       gunzip -c $MPSBIN/${disk_img}.gz | dd bs=1M of=/dev/sdX"
	echo "     You can optionally create persistent /home partition using remaining space on USB disk:"
	echo "       parted --script /dev/sdX -- mkpart primary ext4 $((USB_LIVE_PARTITION_SIZE+1))MiB -1; mkfs.ext4 -L live_phome -O ^has_journal /dev/sdX2"
	echo "     Note: filesystem label \"live_phome\" is _very_ important."
	echo "  2. Update existing USB disk: (which must have been created using method described above)"
	echo "       gunzip -c $MPSBIN/${part_img}.gz | dd bs=1M of=/dev/sdX1"
	echo "     Note: the update image must be of the same size. Sometimes it means you might have to do fresh install."
}

# Generate USB image (BIOS+EFI bootable, GPT partitions, optional persistent /home partition)
make_usb_with_efi() {
	iso="$1"
	disk_img=${iso/.iso/.usbefidisk.img}
	part_img=${iso/.iso/.usbefipart.img}
	size=$((USB_LIVE_PARTITION_SIZE*1024*1024/512))

	echo "Creating a bootable (EFI/BIOS) USB image"
	echo "  Creating empty image of $USB_LIVE_PARTITION_SIZE MiB... (dd)"
	dd if=/dev/zero of=$disk_img bs=512 count=$((size + 4096)) # bs=512: image must be aligned to 512B sector size; +4096=GPT overhead
	sync
	dev=$(losetup --find --show "$disk_img")
	echo "  Creating partitions & FS... (parted, mkfs.vfat)"
	/sbin/parted --script $dev mklabel gpt
	/sbin/parted --script $dev u s mkpart '"EFI System Partition"' fat32 2048 $((2048+size-1)) set 1 boot on set 1 legacy_boot on
	/sbin/udevadm settle
	if [ -f /usr/lib/syslinux/gptmbr.bin ]; then
		cat /usr/lib/syslinux/gptmbr.bin > $dev
	elif [ -f /usr/share/syslinux/gptmbr.bin ]; then
		cat /usr/share/syslinux/gptmbr.bin > $dev
	else
		echo "Could not find gptmbr.bin (have you installed syslinux?)"
		exit 1
	fi
	sleep 5
	sync
	# recreate the device to make sure partition table is refreshed
	losetup -v -d $dev
	dev=$(losetup --find --show -P "$disk_img") # note the -P option which forces partitions to be read and /dev/loop0p1 to be created
	# cheat a little and "rename" the device, so livecd-iso-to-disk will not detect
	# it as a loop device (this would break EFI installation)
	part="/dev/fakeloop1"
	cp -avf ${dev}p1 ${part}
	mkfs.vfat -n MPS_LIVEUSB ${part}
	echo "  Converting iso to live image via ${dev}p1... (livecd-iso-to-disk)"
	livecd-iso-to-disk --efi "$iso" "${part}" || exit 1
	sync
	echo "  Compressing updateable USB live partition image... (gz)"
	dd if=${part} bs=1M | gzip -1 -c > ${part_img}.gz
	losetup -d $dev
	rm ${part}
	echo "  Compressing fresh-install USB disk image... (gz)"
	gzip -f -1 ${disk_img} # xz produces slightly smaller file (<1%), but takes 5-10x more time to compress. gzip is sufficient.
	echo "  Done! Full-disk image ready at $MPSBIN/${disk_img}.gz"
	echo "        Partition image ready at $MPSBIN/${part_img}.gz"
	echo "  1. Fresh install: (!!THIS WILL WIPE WHOLE USB DRIVE!!)"
	echo "       gunzip -c $MPSBIN/${disk_img}.gz | dd bs=1M of=/dev/sdX; sgdisk -e /dev/sdX"
	echo "     You can optionally create persistent /home partition using remaining space on USB disk:"
	echo "       sgdisk -N 2 -t 2:8300 -c 2:\"Persistent Home\" /dev/sdX; mkfs.ext4 -L live_phome -O ^has_journal /dev/sdX2"
	echo "     Note: filesystem label \"live_phome\" is _very_ important."
	echo "  2. Update existing USB disk: (which must have been created using method described above)"
	echo "       gunzip -c $MPSBIN/${part_img}.gz | dd bs=1M of=/dev/sdX1"
	echo "     Note: the update image must be of the same size. Sometimes it means you might have to do fresh install."
}

make_pxe() {
	iso="$1"
	out_tgz=${iso/.iso/.tftpboot.tar.gz}

	echo "Creating a bootable PXE image"
	livecd-iso-to-pxeboot $iso || exit 1

	# add psi customization tool
	mkdir tool
	cp -f $TOPDIR/scripts/psi-customizer.sh tool/psi-customizer.sh
	chmod +x  tool/psi-customizer.sh

	# add version information
	echo "$BUILD_VER" > version

	sync
	tar zcpf $out_tgz tftpboot tool version
	rm -rf tftpboot tool version
	echo "  Done! PXE image ready in $MPSBIN/$out_tgz subdirectory"
}

# install required builddeps
install_image_build_deps || exit 1

# Create directory for storing images
mkdir -p $MPSBIN

# Enter bin directory
cd $MPSBIN

case "$TARGET" in
	mps-all|mps-devel*)
		if [ -z "$SRCISO" ]; then
			echo "Building MPS MAP-devel Live-ISO Image..."
			make_iso "MPS MAP-devel" "mps-devel.ks"
		fi
		;;&

	mps-all|mps-devel)
		echo "Building MPS MAP-devel Live-USB Image..."
		make_usb "$(iso_image_name mps-devel)"
		;;&

	mps-devel-usbefi)
		echo "Building MPS MAP-devel Live-USB Image..."
		make_usb_with_efi "$(iso_image_name mps-host)"
		;;&

	mps-all|mps-map)
		echo "Building MPS MAP Live-ISO Image..."
		make_iso "MPS MAP" "mps-map.ks"
		;;&

	mps-all|mps-psi)
		echo "Building MPS PSI Live-ISO Image..."
		make_iso "MPS PSI" "mps-psi.ks"
		echo "Building MPS PSI PXE Image..."
		make_pxe "$(iso_image_name mps-psi)"
		rm -f "$(iso_image_name mps-psi)"
		;;&

	mps-all|mps-guest)
		if [ -z "$SRCISO" ]; then
			echo "Building MPS Guest VM Live-ISO Image..."
			make_iso "MPS Guest" "mps-guest.ks"
		fi
		echo "Building MPS Guest VM qcow2 Image..."
		make_vm "$(iso_image_name mps-guest)"
		echo "Building MPS Guest VM RPM..."
		make_vm_rpm "$(iso_image_name mps-guest)"
		rm -f "$(iso_image_name mps-guest)"
		;;&

	mps-qual)
		echo "Building MPS QUAL Live-ISO Image..."
		make_iso "MPS QUAL" "mps-qual.ks"
		echo "Building MPS QUAL PXE Image..."
		make_pxe "$(iso_image_name mps-qual)"
		echo "Building MPS QUAL USB Image..."
		make_usb "$(iso_image_name mps-qual)"
		rm -f "$(iso_image_name mps-qual)"
		;;&

	mps-atp)
		echo "Building MPS ATP Live-ISO Image..."
		make_iso "MPS ATP" "mps-atp.ks"
		;;&

esac

echo "$TARGET ready!"
cd $TOPDIR
exit 0

