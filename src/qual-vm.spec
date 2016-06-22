#
# Specifications for the generation of a qual application RPM file
#
Name: qual-vm
Summary: An application used drive simulated MPS hardware on a Virtual Machine
Version: 1.2
Release: 1
License: FILL IN LATER
Group: Applications/Engineering
URL: https://www.fillinlater.com/
Source: https://www.fillinlater.com/qual/stuff/%{name}-%{version}.tar.gz

%description
This spec file is used to generate an RPM of QUAL software for use on a Virtual Machine.  Simulators are included to mimic the behavior of MPS pripherals.

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system/
mkdir -p $RPM_BUILD_ROOT/etc/systemd/system/multi-user.target.wants/
cp qual-vm.service $RPM_BUILD_ROOT/usr/lib/systemd/system/
ln -s /usr/lib/systemd/system/qual-vm.service $RPM_BUILD_ROOT/etc/systemd/system/multi-user.target.wants
mkdir -p $RPM_BUILD_ROOT/thales/qual/src/
cp -r * $RPM_BUILD_ROOT/thales/qual/src/

%files
/usr/lib/systemd/system/qual-vm.service
/etc/systemd/system/multi-user.target.wants/qual-vm.service
/thales/qual/src/*

%post
rm /sbin/mpsinst-makeraid
rm /etc/udev/rules.d/80*
rm /etc/udev/rules.d/95*

%changelog
* Tue Jun 21 2016 Christopher Wallace <cwallace@tklabs.com> 1.1-1
- QUAL-101 : Moved file removal from srcipt to rpm spec file
  (cwallace@tklabs.com)

* Tue Jun 21 2016 Christopher Wallace <cwallace@tklabs.com> 1.0-1
- Initial tito tool tag 

* Tue Jun 21 2016 Christopher Wallace <cwallace@tklabs.com> 1.0-1
- Initial qual-vm RPM
