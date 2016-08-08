#
# Specifications for the generation of a qual application RPM file
#
Name: qual
Summary: An application used drive MPS hardware
Version: 1.25
Release: 1
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: %{name}-%{version}.tar.gz
Requires: python-lxml
Requires: mps-config
Requires: selinux-policy
Requires: rsyslog
Requires: arinc429-driver
Requires: arinc717-driver
Requires: host-domain-device-service
%{?systemd_requires}
BuildRequires: systemd

%package sims
Summary: An application that simulates MPS hardware pripherals
Group: Development/Tools
Requires: %{name} = %{version}

%package ife
Summary: An application that uses a VM to communicate with the MPS IFE card
Group: Applications/Engineering


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
cp systemd/qual-ife.sh %{buildroot}/%{_bindir}/qual-ife
cp systemd/qual-startvm.sh %{buildroot}/thales/host/appliances/qual-startvm
cp systemd/qual*.service %{buildroot}/%{_unitdir}/
cp systemd/50-qual*-service.preset %{buildroot}/usr/lib/systemd/system-preset/
cp scripts/qtemenu.sh %{buildroot}/thales/host/appliances/qtemenu
cp scripts/installifesims.sh %{buildroot}/%{_bindir}/installifesims
cp scripts/genvmconfig.py %{buildroot}/thales/host/appliances/genvmconfig
cp scripts/ifcfg-* %{buildroot}/etc/sysconfig/network-scripts/
cp -r * %{buildroot}/thales/qual/src/


%files
%attr(0755,root,root) /thales/host/appliances/qual*
%attr(0755,root,root) /thales/host/appliances/qtemenu
%attr(0755,root,root) /thales/host/appliances/genvmconfig
%attr(0644,root,root) /%{_unitdir}/qual*.service
%attr(0644,root,root) /usr/lib/systemd/system-preset/50-qual*-service.preset
%attr(0644,root,root) /thales/qual/src/*

%exclude /thales/host/appliances/qual-sims
%exclude /etc/sysconfig/network-scripts
%exclude /%{_unitdir}/qual-sims.service
%exclude /%{_unitdir}/qual-ife.service
%exclude /usr/lib/systemd/system-preset/50-qual-sims-service.preset
%exclude /usr/lib/systemd/system-preset/50-qual-ife-service.preset
%exclude /thales/qual/src/simulator
%exclude /thales/qual/src/systemd
%exclude /thales/qual/src/scripts
%exclude /thales/qual/src/qual/ifeModules
%exclude /thales/qual/src/qual/config/ife.ini

%files sims
%attr(0755,root,root) /thales/host/appliances/qual-sims
%attr(0644,root,root) /%{_unitdir}/qual-sims.service
%attr(0644,root,root) /usr/lib/systemd/system-preset/50-qual-sims-service.preset
%attr(0644,root,root) /thales/qual/src/simulator/*

%exclude /thales/host/appliances/qual
%exclude /thales/host/appliances/qual-startvm
%exclude /thales/host/appliances/qtemenu
%exclude /thales/host/appliances/genvmconfig
%exclude /etc/sysconfig/network-scripts
%exclude /%{_unitdir}/qual.service
%exclude /%{_unitdir}/qual-ife.service
%exclude /%{_unitdir}/qual-startvm.service
%exclude /usr/lib/systemd/system-preset/50-qual-service.preset
%exclude /usr/lib/systemd/system-preset/50-qual-ife-service.preset
%exclude /usr/lib/systemd/system-preset/50-qual-startvm-service.preset
%exclude /thales/qual/src/common
%exclude /thales/qual/src/qual
%exclude /thales/qual/src/systemd
%exclude /thales/qual/src/scripts

%files ife
%attr(0755,root,root) %{_bindir}/*
%attr(0644,root,root) /etc/sysconfig/network-scripts/ifcfg-*
%attr(0644,root,root) /%{_unitdir}/qual-ife.service
%attr(0644,root,root) /usr/lib/systemd/system-preset/50-qual-ife-service.preset
%attr(0644,root,root) /thales/qual/src/*

%exclude /thales/host/appliances
%exclude /%{_unitdir}/qual.service
%exclude /%{_unitdir}/qual-sims.service
%exclude /%{_unitdir}/qual-startvm.service
%exclude /usr/lib/systemd/system-preset/50-qual-service.preset
%exclude /usr/lib/systemd/system-preset/50-qual-sims-service.preset
%exclude /usr/lib/systemd/system-preset/50-qual-startvm-service.preset
%exclude /thales/qual/src/simulator
%exclude /thales/qual/src/systemd
%exclude /thales/qual/src/scripts
%exclude /thales/qual/src/qual/modules
%exclude /thales/qual/src/qual/config/mps.ini
%exclude /thales/qual/src/qual/config/virtualMachine.ini


%post
%systemd_post qual.service
%systemd_post qual-startvm.service
ln -f /thales/qual/src/qual/config/mps.ini /thales/qual/src/qual/config/platform.ini
sed -i -e 's|#$ModLoad imudp|$ModLoad imudp|g' -e 's|#$UDPServerRun 514|$UDPServerRun 514|g' /etc/rsyslog.conf
echo -e "\$ActionQueueFileName fwdRule1\n\$ActionQueueMaxDiskSpace 2g\n\$ActionQueueSaveOnShutdown on\n\$ActionQueueType LinkedList\n\$ActionResumeRetryCount -1\n*.* @192.168.137.1:514" >> /etc/rsyslog.conf
sed -i 's|service_prvkey_file|#service_prvkey_file|g' /thales/host/config/HDDS.conf

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
