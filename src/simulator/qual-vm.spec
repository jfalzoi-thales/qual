#
# Specifications for the generation of a development qual RPM
#
Name: qual-vm
Summary: An application used to simulate MPS hardware on a Virtual Machine
Version: 1.8
Release: 1
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: %{name}-%{version}.tar.gz
Requires: qual
Requires: mps-config
%{?systemd_requires}
BuildRequires: systemd

%description
Implements simulators to act as MPS pripheral devices in order to test QUAL software.

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}/bin/ %{buildroot}/%{_unitdir} %{buildroot}/thales/qual/src/simulator %{buildroot}/usr/lib/systemd/system-preset
install -m755 qual-vm.sh %{buildroot}/bin/
install -m644 qual-vm.service %{buildroot}/%{_unitdir}/
install -m644 50-qual-vm-service.preset %{buildroot}/usr/lib/systemd/system-preset/
cp -r * %{buildroot}/thales/qual/src/simulator/

%files
/bin/qual-vm.sh
/%{_unitdir}/qual-vm.service
/usr/lib/systemd/system-preset/50-qual-vm-service.preset
/thales/qual/src/simulator/*
%exclude /thales/qual/src/simulator/qual-vm.*
%exclude /thales/qual/src/simulator/50-qual-vm-service.preset

%post
%systemd_post qual-vm.service
rm -f /thales/qual/src/qual/config/platform.ini
rm -f /usr/lib/systemd/system-preset/50-mps-drivers.preset
rm -f /etc/systemd/system/mps-drivers.target.wants/*
rm /etc/udev/rules.d/80*
rm /etc/udev/rules.d/95*
ln -s /thales/qual/src/qual/modules/gpio/demo_binaryio.sh /usr/bin/demo_binaryio
ln -s /thales/qual/src/qual/modules/arinc485/demo_serial485.sh /usr/bin/demo_serial485