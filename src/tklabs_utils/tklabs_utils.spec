Summary: TKLabs Utilities Library
Name: tklabs_utils
Version: 1.0.3
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
%exclude %{python2_sitelib}/tklabs_utils/tklabs_utils.spec
%exclude %{python2_sitelib}/tklabs_utils/*/unitTest*
%exclude %{python2_sitelib}/tklabs_utils/tzmq/jsonConversion/readme.md
%exclude %{python2_sitelib}/tklabs_utils/tzmq/jsonConversion/unitTest*

%changelog
* Thu Oct 27 2016 Jenkins <jenkins@tklabs.com> 1.0.3-1
- QUAL-425: Fixed typo (jim.burmeister@tklabs.com)
- QUAL-425: Sneaky fix: CURVE socket doesn't support setting timeout
  (jim.burmeister@tklabs.com)
- QUAL-437 Updated a comment (alberto.treto@tklabs.com)
- QUAL-437 Updated to use http connection and check_output function
  (alberto.treto@tklabs.com)
- QUAL-438 : Sneaky spec file fix (chris.wallace@tklabs.com)
- QUAL-438 : Updated comments (chris.wallace@tklabs.com)
- QUAL-438 : Changed priv to prv (chris.wallace@tklabs.com)
- QUAL-438 : Fixed typos (chris.wallace@tklabs.com)
- QUAL-438 : Added server public key access (chris.wallace@tklabs.com)
- QUAL-438 : Saving work to change branches (chris.wallace@tklabs.com)
- QUAL-438 : Saving work to change branches (chris.wallace@tklabs.com)
- QUAL-433 Fixed msg name and extra line (alberto.treto@tklabs.com)
- QUAL-433 Changed to default value if no timeout was passed
  (alberto.treto@tklabs.com)
- QUAL-427 fixe timeout parameter (alberto.treto@tklabs.com)
- QUAL-427 Add timeout to vtss connection (alberto.treto@tklabs.com)
- QUAL-433 Added timeout to sendRequest functions (alberto.treto@tklabs.com)
- QUAL-288 : Implemented zmq curve authentication on GNMS
  (chris.wallace@tklabs.com)
- QUAL-427 Commented out get switch information. (alberto.treto@tklabs.com)

* Mon Oct 17 2016 Jenkins <jenkins@tklabs.com> 1.0.2-1
- 

* Mon Oct 17 2016 Jenkins <jenkins@tklabs.com> 1.0.1-1
- new package built with tito


