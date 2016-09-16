#
# Specifications for installing I350 programming tools
#
Name: i350tools
Summary: Software to support programming I350 device
Version: 1.0
Release: 1
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: %{name}.tar.gz
Requires: pciutils

%description
This package contains tools and scripts for programming the I350 device.

%prep
%setup -q -n %{name}

%install
mkdir -p %{buildroot}/%{_bindir}
install -m755 bootutil64e %{buildroot}/%{_bindir}
install -m755 eeupdate64e %{buildroot}/%{_bindir}
install -m755 i350-flashtool.sh %{buildroot}/%{_bindir}/i350-flashtool

%files
/%{_bindir}/*
