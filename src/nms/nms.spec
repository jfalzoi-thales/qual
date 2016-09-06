%{!?THALES_BIN_DIR:     %global THALES_BIN_DIR     /thales/host/appliances}
%{!?THALES_CONF_DIR:    %global THALES_CONF_DIR    /thales/host/config}
%{!?THALES_DATA_DIR:    %global THALES_DATA_DIR    /thales/host/data}
%{!?THALES_RUNTIME_DIR: %global THALES_RUNTIME_DIR /thales/host/runtime}

Summary: Network Management Appliance
Name: nms
Version: 1.0.0
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
%{?systemd_requires}
BuildRequires: systemd

%define appdir %{THALES_BIN_DIR}/nms

%define debug_package %{nil}

%description
Network Management Service handles switch and internal communication and configuration.

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}/%{appdir}/ %{buildroot}/%{THALES_CONF_DIR}/ %{buildroot}/%{_unitdir}/
cp -rav * %{buildroot}/%{appdir}
cp -rav config/*.conf %{buildroot}/%{THALES_CONF_DIR}/
cp -rav systemd/*.service %{buildroot}/%{_unitdir}/
ln -s %{appdir}/scripts/GNMS %{buildroot}/%{THALES_BIN_DIR}/GNMS
ln -s %{appdir}/scripts/HNMS %{buildroot}/%{THALES_BIN_DIR}/HNMS
ln -s %{appdir}/scripts/nmsmenu %{buildroot}/%{THALES_BIN_DIR}/nmsmenu
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
%{THALES_BIN_DIR}/GNMS
%{THALES_BIN_DIR}/HNMS
%{THALES_BIN_DIR}/nmsmenu
%{appdir}/GNMS
%{appdir}/HNMS
%{appdir}/nmsmenu
%{appdir}/*/*.py
%{appdir}/*/*/*.py
%{THALES_CONF_DIR}/*
%{_unitdir}/*
%exclude %{appdir}/config
%exclude %{appdir}/systemd
%exclude %{appdir}/*/*.pyc
%exclude %{appdir}/*/*/*.pyc
%exclude %{appdir}/*/*.pyo
%exclude %{appdir}/*/*/*.pyo

%changelog
