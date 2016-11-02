#
# Specifications for the generation of a MPS-IFE for Qual RPM file
#
Name: mps-ife
Summary: Software to support MPS IFE card for Qual
Version: 1.0
Release: 3
License: Proprietary
Group: Applications/Engineering
URL: https://repo-tav.tklabs.com:8102/
Source: %{name}.tar.gz
%{?systemd_requires}
BuildRequires: systemd
BuildRequires: unzip

%description
This package contains drivers and tools for exercising the functionality of the IFE card in the MPS environment.

%prep
%setup -q -n %{name}
mkdir ife-lls-mps
cd ife-lls-mps; rpm2cpio ../dist/ife-lls-mps-%{version}-1.x86_64.rpm | cpio -idm
cd -
mkdir ife_utils
cd ife_utils; unzip ../dist/ife_utils.zip
cd -
mkdir ife_utils_rebuilt
cd ife_utils_rebuilt; tar xf ../dist/ife_utils_rebuilt.tgz

%clean
rm -rf ife-lls-mps ife_utils ife_utils_rebuilt

%install
mkdir -p %{buildroot}/%{_bindir} %{buildroot}/usr/lib64 %{buildroot}/lib/modules %{buildroot}/lib/firmware
install -m755 ife-lls-mps/usr/lib64/libllsapi.so %{buildroot}/usr/lib64/
cp ife-lls-mps/usr/bin/* %{buildroot}/%{_bindir}/
sed -i 's|    pa_loop_enable|    pa_enable $src_kl\n\n    pa_loop_enable|g' %{buildroot}/%{_bindir}/pavaTest.sh
install -m755 ife-lls-mps/lib/modules/i2c-mcp2221.ko %{buildroot}/lib/modules/
install -m755 ife-lls-mps/Sidekick.afx.S19 %{buildroot}/lib/firmware/
install -m755 ife_utils/tkLab/fvt_i2c.sh %{buildroot}/%{_bindir}/
install -m755 ife_utils/tkLab/fvt_z3.sh %{buildroot}/%{_bindir}/
install -m755 ife_utils/tkLab/k60_MAC_code %{buildroot}/%{_bindir}/
install -m755 ife_utils/tkLab/thales_MAC_code %{buildroot}/%{_bindir}/
install -m755 ife_utils_rebuilt/ife_brsw86_uwire %{buildroot}/%{_bindir}/
install -m755 ife_utils_rebuilt/ife_ezport_spi %{buildroot}/%{_bindir}/
install -m755 ife_utils_rebuilt/ife_fpga_uwire %{buildroot}/%{_bindir}/
install -m755 ife_utils_rebuilt/ife_i2c_sel %{buildroot}/%{_bindir}/

%files
/%{_bindir}/*
/lib/firmware/*
/lib/modules/*
/usr/lib64/*
%exclude /%{_bindir}/thales
