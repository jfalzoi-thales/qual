#
# Specifications for installing MPS firmware files
#
Name: mps-firmware
Summary: MPS Firmware files for ATP
Version: 1.0
Release: 4
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: %{name}.tar.gz

%description
This package contains MPS Firmware files for ATP.

%prep
%setup -q -n %{name}

%install
mkdir -p %{buildroot}/thales/qual/firmware
cp firmware/* %{buildroot}/thales/qual/firmware/

%files
/thales/qual/firmware/*
