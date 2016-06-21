#
# Specifications for the generation of a lookbusy application RPM file
#
Name: lookbusy
Summary: An application used to generate synthetic CPU load
Version: 1.4
Release: 1
License: Lookbusy free software, released under terms of GPL
Group: Applications/Emulators
URL: https://www.devin.com/lookbusy/
Source: https://www.devin.com/lookbusy/download/%{name}-%{version}.tar.gz

%description
Lookbusy is a simple application for gnereating synthetic load on a Linux system.  It can generate fixed, predictable loads on CPUs, keep chosen amounts of memeory active, and generate disk traffic in any amounts you need.

%prep
%setup -q -n %{name}-%{version}

%build
sh ./configure --prefix=/usr
make

%install
%make_install

%files
/usr/bin/lookbusy
/usr/share/man/man1/lookbusy.1.gz

%changelog
* Wed Jun 15 2016 Unknown name 1.4-1
- new package built with tito

* Mon Jun 13 2016 Christopher Wallace <cwallace@tklabs.com> 1.4-1
- STUFF HAPPENED