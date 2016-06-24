#
# Specifications for the generation of a qual application RPM file
#
Name: qual
Summary: An application used drive MPS hardware
Version: 1.2
Release: 1
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: %{name}-%{version}.tar.gz
%{?systemd_requires}
BuildRequires: systemd

%description
The MPS Qualification Software is the MPS resident component of an automated test suite designed to exercise the external hardware interfaces and simulate anticipated thermal loading of the LRU.  This is to support system evaluation during environmental and EMI testing scenarios including HALT and HASS.

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}/bin/ %{buildroot}/%{_unitdir} %{buildroot}/thales/qual/src
install -m755 qual.sh %{buildroot}/bin/
install -m644 qual.service %{buildroot}/%{_unitdir}/
cp -r * %{buildroot}/thales/qual/src/
rm -r %{buildroot}/thales/qual/src/simulator
rm %{buildroot}/thales/qual/src/qual.*

%files
/bin/qual.sh
/%{_unitdir}/qual.service
/thales/qual/src/*

%post
%systemd_post qual.service
ln /thales/qual/src/qual/config/mps.ini /thales/qual/src/qual/config/platform.ini

%changelog
* Thu Jun 23 2016 Jenkins <jenkins@tklabs.com> 1.1-1
- QUAL-175 : Made service script paths absolute (jenkins@tklabs.com)
- Automatic commit of package [qual-vm] release [1.0-1]. (jenkins@tklabs.com)

* Thu Jun 23 2016 Jenkins <jenkins@tklabs.com> 1.0-1
- initial tito tag 

* Thu Jun 23 2016 Christopher Wallace <cwallace@tklabs.com> 1.0-1
- Initial qual RPM
