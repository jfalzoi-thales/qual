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
mps-config-psi
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

# Higher level services
machine-manager
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

# QUAL packages
qual
iperf3
lookbusy
alsa-utils
pyserial
fio
pmbw

%end
