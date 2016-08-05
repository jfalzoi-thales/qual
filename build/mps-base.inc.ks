# This file is the base configuration for all targets (host and guest).

# System language
lang en_US.UTF-8

# Keyboard layouts
keyboard us

# System timezone
timezone America/New_York --isUtc

# System authorization information
auth --useshadow --enablemd5

# SELinux configuration
#selinux --enforcing
selinux --permissive

# Firewall configuration
firewall --disabled

# Root password
rootpw --iscrypted $6$1rrnGOTBO8nsgI7u$iPn0CRT49keAqUpCzfV5Q230bCZDGeLQO0OVsrHPpN2Q48fg4twIPSrrn7kFzqNQeTj.oZJ8RDx/y5ewJ4q1T/

# Repository
%include rpm-repos.inc.ks


%post
# regenerate initramfs (in non-hostonly mode to ensure it will work on target machine instead of building one)
KERNEL_VERSION=$(rpm -q kernel --qf '%{version}-%{release}.%{arch}\n')
echo "Regenerating initramfs..."
/sbin/dracut -N -f /boot/initramfs-$KERNEL_VERSION.img $KERNEL_VERSION
%end

# and since livecd-creator first does bootloader config (copies the original initramsfs to /isolinux, etc)
# and then runs post scripts (including the one above which updates initramfs), we need to update it manually
%post --nochroot
# but do this only for livecd (skip for image-creator and rootfs)
# Note: IMAGE_TYPE == livecd cannot be used, since kickstart post scripts are executed with clean env
if [ -n "$LIVE_ROOT" ]; then
    mv -f $(ls $INSTALL_ROOT/boot/initramfs-*.img | grep -v rescue | sort -V | tail -n1) $LIVE_ROOT/isolinux/initrd0.img
fi
%end

