Name:    dtee
Version: 0.0.1
Release: 1%{?dist}
Summary: Run a program with standard output and standard error copied to files

License: GPLv3+
URL:     https://dtee.readthedocs.io/
Source0: https://dl.bintray.com/dtee/source/%{name}-%{version}.tar.gz

BuildRequires: glibc, make, gcc, gcc-c++, boost-devel
BuildRequires: bash, coreutils, diffutils, findutils, grep
BuildRequires: meson >= 0.47.0, ninja-build >= 1.8.2, python2-sphinx >= 1.7

%description
Run a program with standard output and standard error copied to files while
maintaining the original standard output and standard error as normal.

Run a program from cron, suppressing all output unless the process outputs an
error message or has a non-zero exit status whereupon the original output will
be written as normal and the exit code will be appended to standard error.

%global _hardened_build 1

%prep
%setup -q

%build
CFLAGS="%{build_cflags}" \
	CXXFLAGS="%{build_cxxflags}" \
	LDFLAGS="%{build_ldflags}" \
	meson \
	--prefix "%{_prefix}" \
	--bindir "%{_bindir}" \
	--mandir "%{_mandir}" \
	--buildtype=plain \
	--unity on \
	build/redhat

ninja -v -C build/redhat %{_smp_mflags}
ninja -v -C build/redhat test %{_smp_mflags}

%install
DESTDIR="%{buildroot}" ninja -v -C build/redhat install %{_smp_mflags}
ln -sf dtee "%{buildroot}%{_bindir}/cronty"
ln -sf dtee.1 "%{buildroot}%{_mandir}/man1/cronty.1"

%files
%license COPYING
%{_bindir}/dtee
%{_bindir}/cronty
%{_mandir}/man1/dtee.*
%{_mandir}/man1/cronty.*

%changelog
* Sun Nov 11 2018 Simon Arlott <redhat@sa.me.uk> - 0.0.1-1
- Initial release
