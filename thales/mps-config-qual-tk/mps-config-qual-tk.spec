#
# Specifications for the generation of an MPS-config for Qual RPM file
#
Name: mps-config-qual-tk
Summary: QUAL Specific configuration
Version: 1.0.11
Release: 1
Group: System Environment/Libraries
URL: http://www.thalesgroup.com/
Vendor: Thales Avionics, Inc.
License: Proprietary
Source: %{name}-%{version}.tar.gz
Requires: mps-config
%{?systemd_requires}
BuildRequires: systemd

%description
QUAL Specific configuration.

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}/etc/sysconfig/network-scripts/qual
cp network-scripts/* %{buildroot}/etc/sysconfig/network-scripts/qual
touch %{buildroot}/etc/mps-config-qual

%files
/etc/sysconfig/network-scripts/qual/*
/etc/mps-config-qual

%post
cd /etc/sysconfig/network-scripts/ && mv -f qual/* .

