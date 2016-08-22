#!/bin/bash

# Unmount the qual test filesystem if mounted
FS=`mount | fgrep /mnt/qual`
if [ -n "$FS" ]; then
    echo "Unmounting filesystem: $FS"
    umount /mnt/qual
    echo
fi


# show the user drives and RAIDs present in the system
echo "Already running RAIDs:"
mdadm --detail --scan -v


# parse this list and get first four SATA devices
echo
DRIVES="$(lsblk -n -r -S -b -p -o STATE,TRAN,TYPE,NAME | sort | awk '/running usb disk/ { print $4 }' | head -n4)"
if [ $(echo "$DRIVES" | wc -l) -ne 4 ]; then
	echo "Invalid storage configuration; will be unable to create RAIDs! (4x USB disk required)"
fi
# join into single line
DRIVES="$(echo $DRIVES)"


# mdadm output for scanning is multilined; below is a command producing more friendly one-line-per-array output
mdadm_scan_joined_lines() {
	mdadm --detail --scan -v | awk 'BEGIN { l=""; }  /^ARRAY/ { if (l != "") print l; l=""; }  { l = l $0; }  END { if (l != "") print l; }'
}

# stop old arrays
echo "Stopping RAIDs on $DRIVES"
for d in $DRIVES; do
	# complicated scanning-code: be universal and do not require hardcoded names
	if mdadm_scan_joined_lines | grep -q "$d"; then
		echo "  Device '$d' seems to be used in some active arrays; stopping them"
		# stop member arrays first
		mdadm_scan_joined_lines | grep "$d" | grep 'member=' | while read ARRAY raid_dev STUFF; do
			mdadm -S $raid_dev -v || exit 1
		done || exit 1
		# then stop the containers (if still needed)
		mdadm_scan_joined_lines | grep "$d" | while read ARRAY raid_dev STUFF; do
			mdadm -S $raid_dev -v || exit 1
		done || exit 1
		sleep 1
	fi
done
