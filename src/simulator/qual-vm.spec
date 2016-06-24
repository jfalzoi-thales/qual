#
# Specifications for the generation of a development qual RPM
#
Name: qual-vm
Summary: An application used to simulate MPS hardware on a Virtual Machine
Version: 1.0
Release: 1
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: %{name}-%{version}.tar.gz
Requires: qual
%{?systemd_requires}
BuildRequires: systemd

%description
Implements simulators to act as MPS pripheral devices in order to test QUAL software.

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}/bin/ %{buildroot}/%{_unitdir} %{buildroot}/thales/qual/src/simulator
install -m755 qual-vm.sh %{buildroot}/bin/
install -m644 qual-vm.service %{buildroot}/%{_unitdir}/
cp -r * %{buildroot}/thales/qual/src/simulator/
rm %{buildroot}/thales/qual/src/simulator/qual-vm.*

%files
/bin/qual-vm.sh
/%{_unitdir}/qual-vm.service
/thales/qual/src/simulator/*

%post
%systemd_post qual-vm.service
rm -f /thales/qual/src/qual/config/platform.ini
rm -f /etc/systemd/system/multi-user.target.wants/GPIOMgr.service
rm -f /etc/systemd/system/multi-user.target.wants/HDDS.service
rm -f /etc/systemd/system/multi-user.target.wants/I2CDeviceMgr.service
rm -f /etc/systemd/system/multi-user.target.wants/PowerSupplyMonitor.service
rm -f /etc/systemd/system/multi-user.target.wants/SEMADrv.service
rm -f /etc/systemd/system/multi-user.target.wants/SEMAWatchdog.service
rm -f /etc/systemd/system/multi-user.target.wants/RS485-driver.service
rm -f /etc/systemd/system/multi-user.target.wants/RS485Enable.service
rm -f /etc/systemd/system/multi-user.target.wants/RS485Driver.service
rm /sbin/mpsinst-makeraid
rm /etc/udev/rules.d/80*
rm /etc/udev/rules.d/95*

%changelog
