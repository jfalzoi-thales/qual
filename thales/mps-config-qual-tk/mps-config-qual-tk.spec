#
# Specifications for the generation of an MPS-config for Qual RPM file
#
Name: mps-config-qual-tk
Summary: QUAL Specific configuration
Version: 1.0.13
Release: 1
Group: System Environment/Libraries
URL: http://www.thalesgroup.com/
Vendor: Thales Avionics, Inc.
License: Proprietary
Source: %{name}.tar.gz
Requires: mps-config
%{?systemd_requires}
BuildRequires: systemd

%description
QUAL Specific configuration.

%prep
%setup -q -n %{name}

%install
mkdir -p %{buildroot}/opt/config-update %{buildroot}/etc
cp -R network-scripts %{buildroot}/opt/config-update/
touch %{buildroot}/etc/mps-config-qual

%files
/opt/config-update/*
/etc/mps-config-qual

%post
cd /etc/sysconfig/network-scripts && mv -f /opt/config-update/network-scripts/* .
