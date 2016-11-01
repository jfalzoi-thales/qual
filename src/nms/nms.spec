%{!?THALES_BIN_DIR:     %global THALES_BIN_DIR     /thales/host/appliances}
%{!?THALES_CONF_DIR:    %global THALES_CONF_DIR    /thales/host/config}
%{!?THALES_DATA_DIR:    %global THALES_DATA_DIR    /thales/host/data}
%{!?THALES_RUNTIME_DIR: %global THALES_RUNTIME_DIR /thales/host/runtime}

Summary: Network Management Appliance
Name: nms
Version: 1.0.5
Release: 1
Group: System Environment/Libraries
URL: https://repo-tav.tklabs.com:8102/
Vendor: TKLabs
License: Proprietary
Packager: Builder <builder@tklabs.com>
Source: %{name}-%{version}.tar.gz
Requires: python(abi) = 2.7
Requires: python-zmq
Requires: protobuf-python
Requires: tklabs_utils
Requires: i350-tools
Requires: ethtool
%{?systemd_requires}
BuildRequires: systemd

%define appdir %{THALES_BIN_DIR}/nms

%define debug_package %{nil}

%description
Network Management Service handles switch and internal communication and configuration.

%prep
%setup -q -n %{name}-%{version}

%build

%install
mkdir -p %{buildroot}/%{appdir}/ %{buildroot}/%{THALES_CONF_DIR}/ %{buildroot}/%{_unitdir}/ %{buildroot}/usr/lib/systemd/system-preset/
cp -ra * %{buildroot}/%{appdir}/
cp config/*.conf %{buildroot}/%{THALES_CONF_DIR}/
cp systemd/*.service %{buildroot}/%{_unitdir}/
cp systemd/*.preset %{buildroot}/usr/lib/systemd/system-preset/
cp scripts/* %{buildroot}/%{THALES_BIN_DIR}/
sed -i -re 's|__THALES_BIN_DIR__|%{THALES_BIN_DIR}|g' \
    -e 's|__THALES_CONF_DIR__|%{THALES_CONF_DIR}|g' \
    -e 's|__THALES_DATA_DIR__|%{THALES_DATA_DIR}|g' \
    -e 's|__THALES_RUNTIME_DIR__|%{THALES_RUNTIME_DIR}|g' %{buildroot}/%{_unitdir}/*.service
sed -i -re 's|/thales/host/appliances|%{THALES_BIN_DIR}|g' \
    -e 's|/thales/host/config|%{THALES_CONF_DIR}|g' \
    -e 's|/thales/host/data|%{THALES_DATA_DIR}|g' \
    -e 's|/thales/host/runtime|%{THALES_RUNTIME_DIR}|g' %{buildroot}/%{THALES_CONF_DIR}/*.conf

%post
%systemd_post HNMS.service
%systemd_post GNMS.service

%preun
%systemd_preun HNMS.service
%systemd_preun GNMS.service

%postun
%systemd_postun_with_restart HNMS.service
%systemd_postun_with_restart GNMS.service

%files
%attr(0755,root,root) %{THALES_BIN_DIR}/GNMS
%attr(0755,root,root) %{THALES_BIN_DIR}/HNMS
%attr(0755,root,root) %{THALES_BIN_DIR}/nmsmenu
%{appdir}/*
%{THALES_CONF_DIR}/*
%{_unitdir}/*
/usr/lib/systemd/system-preset/*
%exclude %{appdir}/nms.spec
%exclude %{appdir}/proto
%exclude %{appdir}/config
%exclude %{appdir}/systemd
%exclude %{appdir}/scripts

%changelog
* Tue Nov 01 2016 Jenkins <jenkins@tklabs.com> 1.0.5-1
- QUAL-456 Fixed get portName code. (alberto.treto@tklabs.com)
- QUAL-456 Better coding and copied config file to resolve alias.
  (alberto.treto@tklabs.com)
- QUAL-456 Testing alias configuration. (alberto.treto@tklabs.com)

* Mon Oct 31 2016 Jenkins <jenkins@tklabs.com> 1.0.4-1
- QUAL-294 HealthInfoReq module added into host NMS (alberto.treto@tklabs.com)
- QUAL-458 : Updated portInfo to handle 'Link Down' on switch ports
  (chris.wallace@tklabs.com)
- QUAL-412: Save and restore VPD and enable PXE boot when upgrading EEPROM
  (jim.burmeister@tklabs.com)
- QUAL-294 Fixed RPC call and added log info in successful cases
  (alberto.treto@tklabs.com)
- QUAL-294 Implemented upgrade request for switch configuration
  (alberto.treto@tklabs.com)

* Thu Oct 27 2016 Jenkins <jenkins@tklabs.com> 1.0.3-1
- QUAL-455 : Updated addResp in getInVlans (chris.wallace@tklabs.com)
- QUAL-455 : Removed quotes from returned messages (chris.wallace@tklabs.com)
- QUAL-455 : Updated Port Info error descriptions (chris.wallace@tklabs.com)
- QUAL-425: Fixed portResolver entry for front_panel
  (jim.burmeister@tklabs.com)
- QUAL-450: Fixed offsets to I350 EEPROM version number info
  (jim.burmeister@tklabs.com)
- QUAL-450: Refactored version number code and fixed some bugs
  (jim.burmeister@tklabs.com)
- QUAL-448 return vlan IDs according to the port mode.
  (alberto.treto@tklabs.com)
- QUAL-283 Added configurable tftp server path. (alberto.treto@tklabs.com)
- QUAL-425: Added menu item for getting I350 VLANs (jim.burmeister@tklabs.com)
- QUAL-450 : Added MAC Address Logging to HNMS Startup
  (chris.wallace@tklabs.com)
- QUAL-283 Added firmware upgrade to upgrade module. (alberto.treto@tklabs.com)
- QUAL-425: Added support for getting I350 VLANs (jim.burmeister@tklabs.com)
- QUAL-447 : Updated unit test assertions...again. :x
  (chris.wallace@tklabs.com)
- QUAL-447 : Improved unit test assertions (chris.wallace@tklabs.com)
- QUAL-447 : Fixed comment (chris.wallace@tklabs.com)
- QUAL-447 : Made portInfo more efficient (chris.wallace@tklabs.com)
- QUAL-429 Hardcoded fixed value (alberto.treto@tklabs.com)
- QUAL-437 Handled the cases where not version is found.
  (alberto.treto@tklabs.com)
- QUAL-447 : Fixed merge conflict (chris.wallace@tklabs.com)
- QUAL-429 Updated portNames map with the correct tuple
  (alberto.treto@tklabs.com)
- QUAL-447 : Implemented full wildcard handling (chris.wallace@tklabs.com)
- QUAL-437 Updated to use http connection and check_output function
  (alberto.treto@tklabs.com)
- QUAL-447 : Updated wild-card functionality...I think c:
  (chris.wallace@tklabs.com)
- QUAL-439: Fix typos (jim.burmeister@tklabs.com)
- QUAL-439: Added support for PF ports and VF support across PFs
  (jim.burmeister@tklabs.com)
- QUAL-438 : Swapped logic order to improve performance
  (chris.wallace@tklabs.com)
- QUAL-438 : Changed priv to prv (chris.wallace@tklabs.com)
- QUAL-438 : Updated nmsmenu to copy key file if needed
  (chris.wallace@tklabs.com)
- QUAL-437 Log BIO and i350 information (alberto.treto@tklabs.com)
- QUAL-438 : Fixed typos (chris.wallace@tklabs.com)
- QUAL-438 : Fixed typo (chris.wallace@tklabs.com)
- QUAL-438 : Added server public key access (chris.wallace@tklabs.com)
- QUAL-438 : Fixed nms.spec (chris.wallace@tklabs.com)
- QUAL-438 : Fixed path (chris.wallace@tklabs.com)
- QUAL-438 : Added key files for nmsmenu (chris.wallace@tklabs.com)
- QUAL-429 Moved load configuration of enet_8 and i350 to updatePorts
  (alberto.treto@tklabs.com)
- QUAL-448 Select trunk Vlans instead of AccessVlans from json response.
  (alberto.treto@tklabs.com)
- QUAL-438 : Saving work to change branches (chris.wallace@tklabs.com)
- QUAL-429 Removed unnecessary code (alberto.treto@tklabs.com)
- QUAL-429 Update the enet_8 and i350 port names from config file
  (alberto.treto@tklabs.com)
- QUAL-427 Add timeout to vtss connection (alberto.treto@tklabs.com)
- QUAL-432 : Fixed wildcard returned keys (chris.wallace@tklabs.com)
- QUAL-288 : Updated config file (chris.wallace@tklabs.com)
- QUAL-432 Fixed JSON response (alberto.treto@tklabs.com)
- QUAL-284 : Fixed minor bug (chris.wallace@tklabs.com)
- QUAL-288 : Implemented zmq curve authentication on GNMS
  (chris.wallace@tklabs.com)
- QUAL-284: We don't use ethtool in NMS yet but we do use i350-tools
  (jim.burmeister@tklabs.com)
- QUAL-284: Don't need to enable the flash boot flag in NMS - just in ATP
  (jim.burmeister@tklabs.com)
- QUAL-278: Removed unused code (jim.burmeister@tklabs.com)
- QUAL-278: Fixed off-by-one error (jim.burmeister@tklabs.com)
- QUAL-278: Implement VLANAssignReq for VFs (jim.burmeister@tklabs.com)
- QUAL-427 Commented out get switch information. (alberto.treto@tklabs.com)
- QUAL-437 Get the config info from the switch (alberto.treto@tklabs.com)
- QUAL-284 : Implemented NMS Upgrade module (chris.wallace@tklabs.com)
- QUAL-284 : Saving work to change branches (chris.wallace@tklabs.com)

* Mon Oct 17 2016 Jenkins <jenkins@tklabs.com> 1.0.2-1
- QUAL-355 : Fixes for services and portInfo handling
  (chris.wallace@tklabs.com)

* Mon Oct 17 2016 Jenkins <jenkins@tklabs.com> 1.0.1-1
- new package built with tito

