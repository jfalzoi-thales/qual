#
# Specifications for the generation of a qual application RPM file
#
Name: qual
Summary: An application used drive MPS hardware
Version: 1.0
Release: 1
License: FILL IN LATER
Group: Applications/Engineering
URL: https://www.fillinlater.com/
Source: https://www.fillinlater.com/qual/stuff/%{name}-%{version}.tar.gz

%description
Fill in a better description. :D

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system/
mv qual.service $RPM_BUILD_ROOT/usr/lib/systemd/system/
ln -s $RPM_BUILD_ROOT/usr/lib/systemd/system/qual.service $RPM_BUILD_ROOT/etc/systemd/system/multi-user.target.wants/
mkdir -p $RPM_BUILD_ROOT/thales/qual/src/
cp -r * $RPM_BUILD_ROOT/thales/qual/src/

%files
/etc/systemd/system/qual.service
/thales/qual/src/*

%changelog
* Fri Jun 17 2016 Christopher Wallace <cwallace@tklabs.com> 1.0-1
- Tagging with tito tool
* Fri Jun 17 2016 Christopher Wallace <cwallace@tklabs.com> 1.0-1
- Initial Qual RPM
