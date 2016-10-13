Summary: MPS Guest VM Image
Name: mps-guest-vm
Version: RPM_VERSION
Release: 1
License: GPL
Group: Applications/System
URL: http://www.thalesgroup.com
Distribution: Internal
Vendor: Thales Avionics, Inc.
Packager: Builder <builder@thales-ktw.site>
Source0: livecd-mps-guest-RPM_VERSION-stable.vm.qcow2

%description
Sample MPS Guest VM Image

%prep
%build

%install
mkdir -p %{buildroot}/opt/thales/mps/
cp -af %{SOURCE0} %{buildroot}/opt/thales/mps/

%files
/opt/thales/mps/*.vm.qcow2

%changelog
