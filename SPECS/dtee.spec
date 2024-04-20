Name:    dtee
Version: 1.1.1
Release: 1%{?dist}
Summary: Run a program with standard output and standard error copied to files

License: GPLv3+
URL:     https://dtee.readthedocs.io/
Source0: https://dtee.bin.uuid.uk/source/%{name}-%{version}.tar.gz

BuildRequires: glibc, make, gcc, gcc-c++, boost-devel, gettext
BuildRequires: bash, coreutils, diffutils, findutils, grep
BuildRequires: meson >= 1.2.3, ninja-build >= 1.11.1, python3-sphinx >= 1:5.3.0

%description
Run a program with standard output and standard error copied to files while
maintaining the original standard output and standard error as normal.

Can also operate in cron mode (implied when invoked as "cronty"). Suppresses
all output unless the process outputs an error message or has a non-zero exit
status whereupon the original output will be written as normal and the exit
code will be appended to standard error.

%global _default_patch_fuzz 2
%global _hardened_build 1

%prep
%autosetup -p1

%build
CFLAGS="%{build_cflags}" \
	CXXFLAGS="%{build_cxxflags}" \
	LDFLAGS="%{build_ldflags}" \
	meson setup \
	--prefix "%{_prefix}" \
	--bindir "%{_bindir}" \
	--mandir "%{_mandir}" \
	--datadir "%{_datadir}" \
	--buildtype=plain \
	--unity on \
	build/redhat

ninja -v -C build/redhat %{_smp_mflags}
ninja -v -C build/redhat test %{_smp_mflags}

%install
DESTDIR="%{buildroot}" ninja -v -C build/redhat install %{_smp_mflags}
%find_lang %{name}

%files -f %{name}.lang
%license COPYING
%{_bindir}/dtee
%{_bindir}/cronty
%{_mandir}/man1/dtee.*
%{_mandir}/man1/cronty.*

%changelog
* Sat Apr 20 2024 Simon Arlott <redhat@sa.me.uk> - 1.1.1-1
- New version
* Sun May 28 2023 Simon Arlott <redhat@sa.me.uk> - 1.1.0-1
- Initial release
