#
# Specifications for the generation of a development qual RPM
#
Name: qual-vm
Summary: An application used to simulate MPS hardware on a Virtual Machine
Version: 1.0
Release: 1
Requires: qual
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: https://repo-tav.tklabs.com:8102/scm/qual/%{name}.git

%description
Implements simulators to act as MPS pripheral devices in order to test QUAL software.

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p $RPM_BUILD_ROOT/bin/
cp qual-vm.sh $RPM_BUILD_ROOT/bin/
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system/
cp qual-vm.service $RPM_BUILD_ROOT/lib/systemd/system/
mkdir -p $RPM_BUILD_ROOT/thales/qual/src/simulator/
cp -r * $RPM_BUILD_ROOT/thales/qual/src/simulator/
rm $RPM_BUILD_ROOT/thales/qual/src/simulator/qual-vm.*

%files
/bin/qual-vm.sh
/lib/systemd/system/qual-vm.service
/thales/qual/src/simulator/*

%post
ln -s /lib/systemd/system/qual-vm.service /etc/systemd/system/multi-user.target.wants
rm -f /thales/qual/src/qual/config/platform.ini
rm -f /etc/systemd/system/multi-user.target.wants/GPIOMgr.service
rm -f /etc/systemd/system/multi-user.target.wants/HDDS.service
rm -f /etc/systemd/system/multi-user.target.wants/I2CDeviceMgr.service
rm -f /etc/systemd/system/multi-user.target.wants/PowerSupplyMonitor.service
rm -f /etc/systemd/system/multi-user.target.wants/SEMADrv.service
rm -f /etc/systemd/system/multi-user.target.wants/SEMAWatchdog.service
rm -f /etc/systemd/system/multi-user.target.wants/RS485-driver.service
rm -f /etc/systemd/system/multi-user.target.wants/RS485Enable.service
rm /sbin/mpsinst-makeraid
rm /etc/udev/rules.d/80*
rm /etc/udev/rules.d/95*

%changelog
* Thu Jun 23 2016 Jenkins <jenkins@tklabs.com> 1.0-1
- inital tito tag 

* Thu Jun 23 2016 Christopher Wallace <cwallace@tklabs.com> 1.0-1
- Initial qual-vm RPM
