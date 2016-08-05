# Packages
%packages --excludedocs --instLangs=en_US:en:C

kernel
syslinux
vi

# from @base
basesystem
bash
centos-release
coreutils
dhclient
e2fsprogs-libs
filesystem
firewalld
-grubby
gzip
hostname
libselinux
libselinux-utils
policycoreutils
selinux-policy
selinux-policy-targeted
linux-firmware
net-tools
python
rootfiles
rsyslog
tar
wget

# Kernel Modules
kmod-i2c-mcp2221

# FTDI Driver
libftdi

# IFE card Drivers and Tools
mps-ife

# ZeroMQ
libsodium
zeromq4
czmq
python-zmq
protobuf-python

# Development Tools
less
strace

# Qual
qual-ife

%end
