#
# Specifications for the generation of an MPS-config for Qual RPM file
#
Name: mps-config-qual-tk
Summary: QUAL Specific configuration
Version: 1.0.11
Release: 2
Group: System Environment/Libraries
URL: http://www.thalesgroup.com/
Vendor: Thales Avionics, Inc.
License: Proprietary
Source: %{name}.tar.gz
Requires: mps-config
Requires: gpio-manager
Requires: spi-manager
%{?systemd_requires}
BuildRequires: systemd

%description
QUAL Specific configuration.

%prep
%setup -q -n %{name}

%install
mkdir -p %{buildroot}/opt/config-update %{buildroot}/etc
cp -R network-scripts udev-rules host-config %{buildroot}/opt/config-update/
touch %{buildroot}/etc/mps-config-qual

%files
/opt/config-update/*
/etc/mps-config-qual

%post
cd /etc/sysconfig/network-scripts && mv -f /opt/config-update/network-scripts/* .
cd /etc/udev/rules.d && mv -f /opt/config-update/udev-rules/* .
cd /thales/host/config && mv -f /opt/config-update/host-config/* .
