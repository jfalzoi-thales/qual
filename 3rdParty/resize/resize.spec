#
# Specifications for installing resize utility
#
Name: resize
Summary: Resize utility
Version: 1.0
Release: 1
License: MIT
Group: Applications/Engineering
URL: https://www.x.org/
Source: %{name}.tar.gz

%description
This package contains the 'resize' utility from the X11/xterm package

%prep
%setup -q -n %{name}

%install
mkdir -p %{buildroot}/%{_bindir}
install -m755 resize %{buildroot}/%{_bindir}

%files
/%{_bindir}/*
