#
# Specifications for the generation of a qual application RPM file
#
Name: qual
Summary: An application used to drive MPS hardware
Version: 1.45
Release: 1
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: %{name}-%{version}.tar.gz
Requires: python-lxml
Requires: pyserial
Requires: python-netifaces
Requires: python-zmq
Requires: protobuf-python
Requires: mps-config
Requires: selinux-policy
Requires: rsyslog
Requires: host-domain-device-service
%{?systemd_requires}
BuildRequires: systemd

%package sims
Summary: An application that simulates MPS hardware peripherals
Group: Development/Tools
Requires: %{name} = %{version}

%package ife
Summary: An application that uses a VM to communicate with the MPS IFE card
Group: Applications/Engineering
Requires: pyserial
Requires: python-zmq
Requires: protobuf-python


%description
The MPS Qualification Software is the MPS resident component of an automated test suite designed to exercise the external hardware interfaces and simulate anticipated thermal loading of the LRU.  This is to support system evaluation during environmental and EMI testing scenarios including HALT and HASS.

%description sims
This package contains a number of Python driven programs used to simulate ZMQ message communication with hardware peripherals in place of a real MPS.

%description ife
This package runs an IFE virtual machine that is used to communicate with the IFE card on the MPS.


%prep
%setup -q -n %{name}-%{version}


%install
mkdir -p %{buildroot}/%{_bindir} %{buildroot}/etc/sysconfig/network-scripts %{buildroot}/%{_unitdir} %{buildroot}/thales/qual/src %{buildroot}/usr/lib/systemd/system-preset %{buildroot}/thales/host/appliances
cp systemd/qual.sh %{buildroot}/thales/host/appliances/qual
cp systemd/qual-sims.sh %{buildroot}/thales/host/appliances/qual-sims
cp systemd/qual-startvm.sh %{buildroot}/thales/host/appliances/qual-startvm
cp systemd/qual-ife.sh %{buildroot}/%{_bindir}/qual-ife
cp systemd/qual*.service %{buildroot}/%{_unitdir}/
cp systemd/50-qual*-service.preset %{buildroot}/usr/lib/systemd/system-preset/
cp scripts/qtemenu.sh %{buildroot}/thales/host/appliances/qtemenu
cp scripts/installifesims.sh %{buildroot}/%{_bindir}/installifesims
cp scripts/genvmconfig.py %{buildroot}/thales/host/appliances/genvmconfig
cp scripts/ifcfg-* %{buildroot}/etc/sysconfig/network-scripts/
mv %{buildroot}/etc/sysconfig/network-scripts/ifcfg-ens6sk %{buildroot}/etc/sysconfig/network-scripts/ifcfg-ens6:sk
cp -r common/ %{buildroot}/thales/qual/src/
cp -r qual/ %{buildroot}/thales/qual/src/
cp -r simulator/ %{buildroot}/thales/qual/src/


%files
%attr(0755,root,root) /thales/host/appliances/qual
%attr(0755,root,root) /thales/host/appliances/qual-startvm
%attr(0755,root,root) /thales/host/appliances/qtemenu
%attr(0755,root,root) /thales/host/appliances/genvmconfig
%attr(0644,root,root) /%{_unitdir}/qual.service
%attr(0644,root,root) /%{_unitdir}/qual-startvm.service
%attr(0644,root,root) /usr/lib/systemd/system-preset/50-qual-service.preset
%attr(0644,root,root) /usr/lib/systemd/system-preset/50-qual-startvm-service.preset
%attr(0644,root,root) /thales/qual/src/common/*
%attr(0644,root,root) /thales/qual/src/qual/*
%attr(0755,root,root) /thales/qual/src/qual/modules/unittests.sh

%exclude /thales/qual/src/qual/ifeModules
%exclude /thales/qual/src/qual/config/ife.ini

%files sims
%attr(0755,root,root) /thales/host/appliances/qual-sims
%attr(0644,root,root) /%{_unitdir}/qual-sims.service
%attr(0644,root,root) /usr/lib/systemd/system-preset/50-qual-sims-service.preset
%attr(0644,root,root) /thales/qual/src/simulator/*
%attr(0755,root,root) /thales/qual/src/simulator/*.sh

%files ife
%attr(0755,root,root) %{_bindir}/*
%attr(0644,root,root) /etc/sysconfig/network-scripts/ifcfg-*
%attr(0644,root,root) /%{_unitdir}/qual-ife.service
%attr(0644,root,root) /usr/lib/systemd/system-preset/50-qual-ife-service.preset
%attr(0644,root,root) /thales/qual/src/common/*
%attr(0644,root,root) /thales/qual/src/qual/*

%exclude /thales/qual/src/qual/modules
%exclude /thales/qual/src/qual/config/mps.ini
%exclude /thales/qual/src/qual/config/sims.ini


%post
%systemd_post qual.service
%systemd_post qual-startvm.service
ln -f /thales/qual/src/qual/config/mps.ini /thales/qual/src/qual/config/platform.ini
sed -i -e 's|#$ModLoad imudp|$ModLoad imudp|g' -e 's|#$UDPServerRun 514|$UDPServerRun 514|g' /etc/rsyslog.conf
echo -e "\$ActionQueueFileName fwdRule1\n\$ActionQueueMaxDiskSpace 2g\n\$ActionQueueSaveOnShutdown on\n\$ActionQueueType LinkedList\n\$ActionResumeRetryCount -1\n*.* @192.168.137.1:514" >> /etc/rsyslog.conf
sed -i -e 's|service_prvkey_file|#service_prvkey_file|g' -e 's|tcp://192.168.1.4:40001|tcp://*:40001|g' /thales/host/config/HDDS.conf

%posttrans
ln -s ../default.xml /etc/libvirt/qemu/networks/autostart/default.xml
sed -i 's|SELINUX=enforcing|SELINUX=permissive|g' /etc/selinux/config

%post sims
%systemd_post qual-sims.service
rm -f /thales/qual/src/qual/config/platform.ini
rm -f /usr/lib/systemd/system-preset/50-mps-drivers.preset
rm -f /etc/systemd/system/mps-drivers.target.wants/*
rm -f /etc/udev/rules.d/80*
rm -f /etc/udev/rules.d/95*

%post ife
%systemd_post qual-ife.service
ln -f /thales/qual/src/qual/config/ife.ini /thales/qual/src/qual/config/platform.ini
