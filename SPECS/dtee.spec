Name:    dtee
Version: 1.0.1
Release: 1%{?dist}
Summary: Run a program with standard output and standard error copied to files

License: GPLv3+
URL:     https://dtee.readthedocs.io/
Source0: https://dtee.bin.uuid.uk/source/%{name}-%{version}.tar.gz
Source1: https://github.com/boostorg/asio/commit/749e9d221960c6703220eaf4c99b6ee913db7607.patch

# rhel-6-server-rpms
BuildRequires: glibc, make, gcc, gcc-c++
BuildRequires: bash, coreutils, diffutils, findutils, grep
BuildRequires: scl-utils, scl-utils-build

# rhel-server-rhscl-6-rpms
BuildRequires: %scl_require_package devtoolset-7 gcc
BuildRequires: %scl_require_package devtoolset-7 gcc-c++
BuildRequires: rh-python36
BuildRequires: %scl_require_package rh-python36 python-virtualenv
BuildRequires: %scl_require_package rh-mongodb34 boost-devel >= 1.55

Requires: %scl_require_package rh-mongodb34 boost-system
Requires: %scl_require_package rh-mongodb34 boost-filesystem
Requires: %scl_require_package rh-mongodb34 boost-program-options

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
sed -e "s@link_args: link_args,@link_args: link_args, build_rpath: '/opt/rh/rh-mongodb34/root%{_libdir}', install_rpath: '/opt/rh/rh-mongodb34/root%{_libdir}',@" -i meson.build

set +e
source scl_source enable rh-python36
RET=$?
set -e
if [ $RET -ne 0 ]; then
	echo SCL missing
	exit 1
fi

virtualenv build/virtualenv/dtee
build/virtualenv/dtee/bin/python3 build/virtualenv/dtee/bin/pip install \
	--upgrade pip==8.1.1 --no-deps --ignore-installed
build/virtualenv/dtee/bin/python3 build/virtualenv/dtee/bin/pip install \
	meson==0.48.2 \
	ninja==1.8.2 \
	Jinja2==2.10 \
	snowballstemmer==1.2.1 \
	alabaster==0.7.12 \
	Pygments==2.2.0 \
	Babel==2.6.0 \
	docutils==0.14 \
	six==1.11.0 \
	sphinx-rtd-theme==0.4.2 \
	MarkupSafe==1.1.0 \
	pytz==2018.7 \
	Sphinx==1.3.6 \
	--no-deps --ignore-installed

%build
set +e
source scl_source enable devtoolset-7 rh-python36
RET=$?
set -e
if [ $RET -ne 0 ]; then
	echo SCL missing
	exit 1
fi

export BOOST_ROOT="/opt/rh/rh-mongodb34/root%{_prefix}"
export BOOST_INCLUDEDIR="/opt/rh/rh-mongodb34/root%{_includedir}"
export BOOST_LIBRARYDIR="/opt/rh/rh-mongodb34/root%{_libdir}"

VENV_DTEE_BIN="$PWD/build/virtualenv/dtee/bin"
PATH="$VENV_DTEE_BIN:$PATH" \
	CFLAGS="$RPM_OPT_FLAGS" \
	CXXFLAGS="$RPM_OPT_FLAGS" \
	LDFLAGS="$RPM_LD_FLAGS" \
	meson \
	--prefix "%{_prefix}" \
	--bindir "%{_bindir}" \
	--mandir "%{_mandir}" \
	--buildtype=plain \
	--unity on \
	build/redhat

PATH="$VENV_DTEE_BIN:$PATH" ninja -v -C build/redhat %{_smp_mflags}
PATH="$VENV_DTEE_BIN:$PATH" ninja -v -C build/redhat test %{_smp_mflags}

%install
set +e
source scl_source enable devtoolset-7 rh-python36
RET=$?
set -e
if [ $RET -ne 0 ]; then
	echo SCL missing
	exit 1
fi

VENV_DTEE_BIN="$PWD/build/virtualenv/dtee/bin"
PATH="$VENV_DTEE_BIN:$PATH" DESTDIR="%{buildroot}" ninja -v -C build/redhat install %{_smp_mflags}
ln -sf dtee "%{buildroot}%{_bindir}/cronty"
ln -sf dtee.1 "%{buildroot}%{_mandir}/man1/cronty.1"

%files
%doc COPYING
%{_bindir}/dtee
%{_bindir}/cronty
%{_mandir}/man1/dtee.*
%{_mandir}/man1/cronty.*

%changelog
* Sat Dec 22 2018 Simon Arlott <redhat@sa.me.uk> - 1.0.1-1
- New version
* Sun Dec 09 2018 Simon Arlott <redhat@sa.me.uk> - 1.0.0-1
- New version
* Tue Nov 13 2018 Simon Arlott <redhat@sa.me.uk> - 0.0.1-1
- Initial release
