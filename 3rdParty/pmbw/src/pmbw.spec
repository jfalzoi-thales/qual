#
# Specifications for the generation of a pmbw application RPM file
#
Name: pmbw
Summary: The pmbw is a set of assembler routines to measure the parallell memory (cache and RAM) bandwidth of modern multi-core machines.
Version: 0.6.2
Release: 1
License: pmbw is free software, released under terms of GPL
Group: Applications/Emulators
URL: https://panthema.net/2013/pmbw/index.html
Source: https://panthema.net/2013/pmbw/%{name}-%{version}.tar.gz

%description
The tool pmbw is a set of assembler routines to measure the parallel memory (cache and RAM) bandwidth of modern multi-core machines.  Memory bandwidth is one of the key performance factors of any computer system.  And today, measureing the memory performance often gives a more realistic view on the overall speed of a machine than pure arithmetic or floating-point benchmarks.  This is due to the speed of computation units in modern CPUs growing faster than the memory bandwidth, which however is required to get more information to the CPU.  The bigger the processed data amount gets, the more important memory bandwidth becomes!

%prep
%setup -q -n %{name}-%{version}

%build
sh ./configure --prefix=/usr
make

%install
%make_install

%files
/usr/bin/pmbw
/usr/bin/stats2gnuplot

%changelog
* Tue Jun 21 2016 Christopher Wallace <cwallace@tklabs.com> 0.6.2-1
- Initial tito tool tag 

* Tue Jun 21 2016 Christopher Wallace <cwallace@tklabs.com> 0.6.2
- Created pmbw.spec file
