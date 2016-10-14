Summary: TKLabs Utilities Library
Name: tklabs_utils
Version: 1.0.0
Release: 1
Group: System Environment/Libraries
URL: https://repo-tav.tklabs.com:8102/
Vendor: TKLabs
License: Proprietary
Packager: Builder <builder@tklabs.com>
Source: %{name}-%{version}.tar.gz
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
%exclude %{python2_sitelib}/tklabs_utils/*/unitTest*
%exclude %{python2_sitelib}/tklabs_utils/tzmq/jsonConversion/readme.md
%exclude %{python2_sitelib}/tklabs_utils/tzmq/jsonConversion/unitTest*

%changelog

