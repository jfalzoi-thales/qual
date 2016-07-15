# Packages
%packages --excludedocs --instLangs=en_US:en:C

kernel
syslinux
vi

#from @base
basesystem
bash
bzip2
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
openssh-server
openssh-clients
python
rootfiles
rsyslog
tar
unzip
wget
xz
zip

# kernel modules
kmod-i2c-mcp2221

# mps config, tools and libs
mps-config
mps-tools
mpsinst-tools
libmps-utils

# SEMA Driver
libsema
sema-driver

# FTDI driver
libftdi

# I2C Manager
i2c-device-manager

# GPIO Manager
gpio-manager

# Power Supply Monitor
power-supply-monitor

# ARINC drivers
arinc429-driver
arinc717-driver

# Higher level services
host-domain-device-service


# TPM packages
trousers
tpm-tools

# ZeroMQ
libsodium
zeromq4
czmq
python-zmq
protobuf-python

# Qual
qual
#qual-vm
iperf3
lookbusy
alsa-utils
pyserial
fio
pmbw
ethtool
pciutils

%end
