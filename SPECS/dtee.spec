Name:    dtee
Version: 1.1.0
Release: 2%{?dist}
Summary: Run a program with standard output and standard error copied to files

License: GPLv3+
URL:     https://dtee.readthedocs.io/
Source0: https://dtee.bin.uuid.uk/source/%{name}-%{version}.tar.gz

# rhel-8-for-x86_64-baseos-rpms
# rhel-8-for-x86_64-appstream-rpms
BuildRequires: glibc, make, gcc, gcc-c++, boost-devel, gettext
BuildRequires: bash, coreutils, diffutils, findutils, grep

# codeready-builder-for-rhel-8-x86_64-rpms
BuildRequires: meson >= 0.58.2, ninja-build >= 1.8.2, python3-sphinx >= 1:1.7.6

%description
Run a program with standard output and standard error copied to files while
maintaining the original standard output and standard error as normal.

Can also operate in cron mode (implied when invoked as "cronty"). Suppresses
all output unless the process outputs an error message or has a non-zero exit
status whereupon the original output will be written as normal and the exit
code will be appended to standard error.

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
	--datadir "%{_datadir}" \
	--buildtype=plain \
	--unity on \
	build/redhat

ninja -v -C build/redhat %{_smp_mflags}
ninja -v -C build/redhat test %{_smp_mflags}

%install
DESTDIR="%{buildroot}" ninja -v -C build/redhat install %{_smp_mflags}
ln -sf dtee "%{buildroot}%{_bindir}/cronty"
ln -sf dtee.1 "%{buildroot}%{_mandir}/man1/cronty.1"
%find_lang %{name}

%files -f %{name}.lang
%license COPYING
%{_bindir}/dtee
%{_bindir}/cronty
%{_mandir}/man1/dtee.*
%{_mandir}/man1/cronty.*

%changelog
* Sun May 30 2021 Simon Arlott <redhat@sa.me.uk> - 1.1.0-1
- New version
* Sun Jun 09 2019 Simon Arlott <redhat@sa.me.uk> - 1.0.1-1
- Initial release
