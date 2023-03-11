Name:    dtee
Version: 1.1.0
Release: 1%{?dist}
Summary: Run a program with standard output and standard error copied to files

License: GPLv3+
URL:     https://dtee.readthedocs.io/
Source0: https://dtee.bin.uuid.uk/source/%{name}-%{version}.tar.gz
Patch1:  https://github.com/nomis/dtee/commit/648f908f7a43b987fb5d5e291b0f101ee61a393f.patch
Patch2:  https://github.com/nomis/dtee/commit/d3a7a5647ce33696f0be7b7ad78828980a340fd2.patch
Patch3:  https://github.com/nomis/dtee/commit/5f73c669ed8551a11c8cc316acf91e49b221d97c.patch
Patch4:  https://github.com/nomis/dtee/commit/04bf093a47991e8885384c1c140b7ac9212964a7.patch
Patch5:  https://github.com/nomis/dtee/commit/2c31a3b0ab6b1499f5edb103a58fd35ee76b5b46.patch
Patch6:  https://github.com/nomis/dtee/commit/07943309225ff005aaf83cae361ee71aff0610e5.patch
Patch7:  https://github.com/nomis/dtee/commit/58631255276693626cd06002577f4654c11fe496.patch
Patch8:  https://github.com/nomis/dtee/commit/a7611ff355afa0e07e66609bf2c9198f37bb0799.patch

BuildRequires: glibc, make, gcc, gcc-c++, boost-devel, gettext
BuildRequires: bash, coreutils, diffutils, findutils, grep
BuildRequires: meson >= 1.0.0, ninja-build >= 1.10.2, python3-sphinx >= 1:5.0.2

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
* Sat Mar 11 2023 Simon Arlott <redhat@sa.me.uk> - 1.1.0-1
- Initial release
