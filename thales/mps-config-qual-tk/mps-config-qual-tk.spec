#
# Specifications for the generation of an MPS-config for Qual RPM file
#
Name: mps-config-qual-tk
Summary: QUAL Specific configuration
Version: 1.0.14
Release: 2
Group: System Environment/Libraries
URL: http://www.thalesgroup.com/
Vendor: Thales Avionics, Inc.
License: Proprietary
Source: %{name}.tar.gz
Requires: mps-config
Requires: selinux-policy
Requires: rsyslog
Requires: host-domain-device-service
%{?systemd_requires}
BuildRequires: systemd

%description
QUAL Specific configuration.

%prep
%setup -q -n %{name}

%install
mkdir -p %{buildroot}/opt/config-update %{buildroot}/etc
cp -R network-scripts %{buildroot}/opt/config-update/
cp -R units %{buildroot}/opt/config-update/
touch %{buildroot}/etc/mps-config-qual

%files
/opt/config-update/*
/etc/mps-config-qual

%post
cd /etc/sysconfig/network-scripts && mv -f /opt/config-update/network-scripts/* .
cd %{_unitdir} && mv -f /opt/config-update/units/* .
sed -i '/enable CPUEthernet.service/d' /usr/lib/systemd/system-preset/50-mps-drivers.preset
sed -i -e 's|#$ModLoad imudp|$ModLoad imudp|g' -e 's|#$UDPServerRun 514|$UDPServerRun 514|g' /etc/rsyslog.conf
sed -i -e 's|service_prvkey_file|#service_prvkey_file|g' -e 's|tcp://192.168.1.4:40001|tcp://*:40001|g' /thales/host/config/HDDS.conf

%posttrans
ln -s ../default.xml /etc/libvirt/qemu/networks/autostart/default.xml
sed -i 's|SELINUX=enforcing|SELINUX=permissive|g' /etc/selinux/config
