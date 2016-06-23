#
# Specifications for the generation of a qual application RPM file
#
Name: qual
Summary: An application used drive MPS hardware
Version: 1.0
Release: 1
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: https://repo-tav.tklabs.com:8102/scm/qual/%{name}.git

%description
The MPS Qualification Software is the MPS resident component of an automated test suite designed to exercise the external hardware interfaces and simulate anticipated thermal loading of the LRU.  This is to support system evaluation during environmental and EMI testing scenarios including HALT and HASS.

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p $RPM_BUILD_ROOT/bin/
cp qual.sh $RPM_BUILD_ROOT/bin/
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system/
cp qual.service $RPM_BUILD_ROOT/lib/systemd/system/
mkdir -p $RPM_BUILD_ROOT/thales/qual/src/
cp -r * $RPM_BUILD_ROOT/thales/qual/src/
rm -r $RPM_BUILD_ROOT/thales/qual/src/simulator
rm $RPM_BUILD_ROOT/thales/qual/src/qual.*

%files
/bin/qual.sh
/lib/systemd/system/qual.service
/thales/qual/src/*

%post
ln -s /lib/systemd/system/qual.service /etc/systemd/system/multi-user.target.wants
ln /thales/qual/src/qual/config/mps.ini /thales/qual/src/qual/config/platform.ini

%changelog
* Thu Jun 23 2016 Jenkins <jenkins@tklabs.com> 1.0-1
- initial tito tag 

* Thu Jun 23 2016 Christopher Wallace <cwallace@tklabs.com> 1.0-1
- Initial qual RPM
