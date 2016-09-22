#
# Specifications for the generation of an MPS-config for Qual/ATP RPM file
#
Name: mps-config-qual-tk
Summary: QUAL/ATP Specific configuration
Version: 1.0.14
Release: 4
Group: System Environment/Libraries
URL: http://www.thalesgroup.com/
Vendor: Thales Avionics, Inc.
License: Proprietary
Source: %{name}.tar.gz
Requires: mps-config
Requires: selinux-policy
Requires: rsyslog
Requires: tftp-server
Requires: xinetd
Requires: host-domain-device-service
%{?systemd_requires}
BuildRequires: systemd

%description
QUAL/ATP Specific configuration.

%prep
%setup -q -n %{name}

%install
mkdir -p %{buildroot}/opt/config-update %{buildroot}/etc
cp -R network-scripts %{buildroot}/opt/config-update/
touch %{buildroot}/etc/mps-config-qual
touch %{buildroot}/etc/mps-config-atp

%files
/opt/config-update/*
/etc/mps-config-*

%post
cd /etc/sysconfig/network-scripts && mv -f /opt/config-update/network-scripts/* .
sed -i '/enable CPUEthernet.service/d' /usr/lib/systemd/system-preset/50-mps-drivers.preset
sed -i -e 's|#$ModLoad imudp|$ModLoad imudp|g' -e 's|#$UDPServerRun 514|$UDPServerRun 514|g' /etc/rsyslog.conf
sed -i -e 's|service_prvkey_file|#service_prvkey_file|g' -e 's|tcp://192.168.1.4:40001|tcp://*:40001|g' /thales/host/config/HDDS.conf
sed -i -e 's|-s|-c -s|g' -e 's|disable\([ \t]*\)= yes|disable\1= no|g' -e 's|/var/lib/tftpboot|/thales/qual/firmware|g' /etc/xinetd.d/tftp
rmdir /var/lib/tftpboot
ln -s /thales/qual/firmware /var/lib/tftpboot

%posttrans
ln -s ../default.xml /etc/libvirt/qemu/networks/autostart/default.xml
sed -i 's|SELINUX=enforcing|SELINUX=permissive|g' /etc/selinux/config
