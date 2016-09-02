Summary: TKLabs Utilities Library
Name: tklabs_utils
Version: 1.0.2
Release: 1
Group: System Environment/Libraries
URL: https://repo-tav.tklabs.com:8102/
Vendor: TKLabs
License: Proprietary
Packager: TKLabs <placeholder@tklabs.com>
Source: %{name}-%{version}.tar.gz
Requires: python(abi) = 2.7
BuildRequires: python2-devel

%description
Library used in the implementation of TKLabs developed software

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}/%{python2_sitelib}/tklabs_utils/
cp -r * %{buildroot}/%{python2_sitelib}/tklabs_utils/

%files
%{python2_sitelib}/tklabs_utils/

%changelog
* Fri Sep 02 2016 Christopher Wallace <chris.wallace@tklabs.com> 1.0.2-1
- 

* Fri Sep 02 2016 Christopher Wallace <chris.wallace@tklabs.com> 1.0.1-1
- new package built with tito

