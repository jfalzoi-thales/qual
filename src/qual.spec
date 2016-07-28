#
# Specifications for the generation of a qual application RPM file
#
Name: qual
Summary: An application used drive MPS hardware
Version: 1.14
Release: 1
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: %{name}-%{version}.tar.gz
Requires: rsyslog
Requires: arinc429-driver
Requires: arinc717-driver
Requires: host-domain-device-service
%{?systemd_requires}
BuildRequires: systemd

%description
The MPS Qualification Software is the MPS resident component of an automated test suite designed to exercise the external hardware interfaces and simulate anticipated thermal loading of the LRU.  This is to support system evaluation during environmental and EMI testing scenarios including HALT and HASS.

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}/bin/ %{buildroot}/%{_unitdir} %{buildroot}/thales/qual/src %{buildroot}/usr/lib/systemd/system-preset
mkdir -p %{buildroot}/thales/host/appliances
install -m755 qual.sh %{buildroot}/bin/
install -m755 qual/qte/qtemenu.sh %{buildroot}/thales/host/appliances/qtemenu
install -m644 qual.service %{buildroot}/%{_unitdir}/
install -m644 50-qual-service.preset %{buildroot}/usr/lib/systemd/system-preset/
cp -r * %{buildroot}/thales/qual/src/

%files
/bin/qual.sh
/%{_unitdir}/qual.service
/usr/lib/systemd/system-preset/50-qual-service.preset
/thales/qual/src/*
/thales/host/appliances/qtemenu
%exclude /thales/qual/src/simulator
%exclude /thales/qual/src/qual.*
%exclude /thales/qual/src/50-qual-service.preset
%exclude /thales/qual/src/qual/qte/qtemenu.sh

%post
%systemd_post qual.service
ln -f /thales/qual/src/qual/config/mps.ini /thales/qual/src/qual/config/platform.ini
echo -e "\$ActionQueueFileName fwdRule1\n\$ActionQueueMaxDiskSpace 2g\n\$ActionQueueSaveOnShutdown on\n\$ActionQueueType LinkedList\n\$ActionResumeRetryCount -1\n*.* @192.168.137.1:514" >> /etc/rsyslog.conf
sed -i 's|arinc429drv|arinc429drv -l VERBOSE|g' /usr/lib/systemd/system/arinc429drv.service
sed -i 's|service_prvkey_file|#service_prvkey_file|g' /thales/host/config/HDDS.conf
ln -s /thales/qual/src/qual/modules/gpio/demo_binaryio.sh /usr/bin/demo_binaryio
ln -s /thales/qual/src/qual/modules/arinc485/demo_serial485.sh /usr/bin/demo_serial485
