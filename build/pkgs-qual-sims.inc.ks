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
kmod-e1000e

# mps config, tools and libs
mps-config
#mps-config-qual
#mps-config-qual-tk
#mps-keys
#mps-tools
mpsinst-tools
#libmps-utils

# SEMA Driver
#libsema
#sema-driver

# FTDI driver
libftd2xx
libftdi

# I2C Manager
#i2c-device-manager

# GPIO Manager
#gpio-manager

# SPI Manager
#spi-manager

# ARINC Drivers
#arinc429-driver
#arinc717-driver

# RTC Driver
#rtc-driver

# Power Supply Monitor
#power-supply-monitor

# MAP test tools
#test-tools
#arinc717-driver-tests

# Higher level services
host-domain-device-service
fake-nms


# TPM packages
#trousers
#tpm-tools

# ZeroMQ
libsodium
zeromq4
czmq
python-zmq
protobuf-python

# Development Tools
less
pciutils
strace
usbutils
setserial

# Qual
qual
qual-sims
iperf3
lookbusy
alsa-utils
pyserial
fio
pmbw
ethtool
mps-guest-vm

%end
