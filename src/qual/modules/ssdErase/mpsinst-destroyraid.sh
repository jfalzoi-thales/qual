#!/bin/bash

# script expects two arguments: target size of "protected" RAID in GiB (min. 10)
# and optionally 'YES,CLEAR_MY_DISKS' confirmation string for unattended creation
if [ -z "$1" ] || [[ ! "$1" =~ ^[0-9]+$ ]] || [ $1 -lt 10 ]; then
	echo "Need proper arguments!"
	echo "Example usage:"
	echo -e "\t$0 100 YES,CLEAR_MY_DISKS"
	echo
	echo "where '100' is the mandatory protected RAID size in GiB (min. 10GiB)"
	echo "and 'YES,CLEAR_MY_DISKS' is an optional literal string confirming you understand this script will:"
	echo "  - stop and destroy MD RAIDs currently running on auto-selected devices"
	echo "  - wipe all user data, file systems and partitions on auto-selected devices"
	echo "Providing the confirmation string as second argument will make the script non-interactive."
	echo
	echo "The script detects disks automatically; first 4 SATA drives found are used."
	echo "If the disks are different (not the same vendor/model), typical RAID restrictions apply:"
	echo "  - smallest drive determines RAID size;"
	echo "  - slowest drive determines RAID speed."
	echo "Also note that if disks currently contain some filesystems/logical volumes, they must not be mounted."
	exit 1
fi

# show the user drives and RAIDs present in the system
echo "Detected following disks:"
lsblk -S -p -o TRAN,TYPE,HCTL,NAME,SIZE,VENDOR,MODEL,SERIAL,REV,STATE,RA,RO,RM,ROTA,PHY-SEC,LOG-SEC,DISC-GRAN,SCHED

echo
echo "Already running RAIDs:"
mdadm --detail --scan -v

# ensure LVM caches are fresh
pvscan --cache
vgscan --cache
echo "Detected LVM volume groups:"
lvs -o lv_name,vg_name,lv_attr,lv_size,lv_tags,lv_time,seg_pe_ranges
echo "Detected LVM logical volumes:"
vgs


# parse this list and get first four SATA devices
echo
echo "Chosing disks for RAID..."
DRIVES="$(lsblk -n -r -S -b -p -o STATE,TRAN,TYPE,NAME | sort | awk '/running sata disk/ { print $4 }' | head -n4)"
if [ $(echo "$DRIVES" | wc -l) -ne 4 ]; then
	echo "Invalid storage configuration; unable to create RAIDs! (4x SATA disk required)"
	exit 1
fi
# join into single line
DRIVES="$(echo $DRIVES)"

# issue a warning and give user a chance to stop the process
echo
echo "Chosen following drives for making RAIDs:"
echo "  $DRIVES"
echo

# ask for confirmation if no confirmation string detected
if [ "$2" != "YES,CLEAR_MY_DISKS" ]; then
	echo "This script is dangerous and will DESTROY all current data on selected drives!"
	echo -n "Continue? [y/N] "
	read ANSWER
	if [ "$ANSWER" != "y" -a "$ANSWER" != "Y" -a "$ANSWER" != "yes" ]; then
		echo "Exiting without touching anything!"
		exit 1
	fi
else
	# if there is the confirmation string, just give some short opportunity to stop before it's too late
	echo "THIS WILL DESTROY ALL DATA ON THESE DRIVES!"
	echo
	echo "... last chance for CTRL+C ..."
	sleep 3
fi


# mdadm output for scanning is multilined; below is a command producing more friendly one-line-per-array output
mdadm_scan_joined_lines() {
	mdadm --detail --scan -v | awk 'BEGIN { l=""; }  /^ARRAY/ { if (l != "") print l; l=""; }  { l = l $0; }  END { if (l != "") print l; }'
}

# reset disks - clear old raids: stop running VGs if nothing is mounted, wipe old partition tables, filesystems, etc.
echo
echo "Destroing old volume groups and partition tables on $DRIVES"
for d in /dev/md/raid_protected_0 /dev/md/raid_unprotected_0; do
	[ -b $d ] || continue

	for pv in $(blkid -t TYPE=LVM2_member -o device ${d}*); do
		IN_VG="$(echo $(pvs --noheadings --nosuffix -o vg_name $pv 2>/dev/null))"
		if [ -n "$IN_VG" ]; then
			echo "Destroying VG $IN_VG to which RAID device $pv belongs..."
			vgchange -a n $IN_VG || exit 1
			vgremove -ff $IN_VG || exit 1
		fi
		pvremove -y $pv || exit 1
	done

	wipefs -a $d
	dd if=/dev/zero of=$d status=none bs=512 count=16384
	dd if=/dev/zero of=$d status=none bs=512 count=16384 seek=$(($(blockdev --getsz $d) - 16384))
done

# wait a while, refresh caches
sync
udevadm settle || true
pvscan --cache
vgscan --cache

# reset disks - wipe old arrays and partition tables
echo
echo "Stopping old RAIDs on $DRIVES"
for d in $DRIVES; do
	# complicated scanning-code: be universal and do not require hardcoded names
	if mdadm_scan_joined_lines | grep -q "$d"; then
		echo "  Device '$d' seems to be used in some active arrays; stopping them first"
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

echo
echo "Destroing old RAIDs and partition tables on $DRIVES"
for d in $DRIVES; do
	wipefs -a $d
	dd if=/dev/zero of=$d status=none bs=512 count=16384
	dd if=/dev/zero of=$d status=none bs=512 count=16384 seek=$(($(blockdev --getsz $d) - 16384))
	blkdiscard -v $d
done
sleep 1

echo
echo "Syncing..."
sync