# Packages
%packages --excludedocs --instLangs=en_US:en:C

kernel
syslinux
vi

# from @base
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

# Kernel Modules
kmod-i2c-mcp2221

# MPS Config, Tools and Libs
mps-config
#mps-config-qual
#mps-config-map
mps-keys
mps-tools
mpsinst-tools
libmps-utils

# SEMA Driver
libsema
sema-driver

# FTDI Driver
libftdi

# I2C manager
i2c-device-manager

# GPIO Manager
gpio-manager

# SPI Manager
spi-manager

# Power Supply Monitor
power-supply-monitor

# ARINC Drivers
arinc429-driver
arinc717-driver

# Higher Level Services
host-domain-device-service

# TPM Packages
trousers
tpm-tools

# ZeroMQ
libsodium
zeromq4
czmq
python-zmq
protobuf-python

# Development Tools
less
minicom
pciutils
strace
usbutils

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

%end