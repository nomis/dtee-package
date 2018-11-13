Name:    dtee
Version: 0.0.1
Release: 1%{?dist}
Summary: Run a program with standard output and standard error copied to files

License: GPLv3+ 
URL:     https://dtee.readthedocs.io/
Source0: https://dl.bintray.com/dtee/source/%{name}-%{version}.tar.gz
Source1: https://github.com/boostorg/asio/commit/749e9d221960c6703220eaf4c99b6ee913db7607.patch

# rhel-7-server-rpms
BuildRequires: glibc, make, gcc, gcc-c++, boost-devel
BuildRequires: bash, coreutils, diffutils, findutils, grep
BuildRequires: scl-utils

# rhel-server-rhscl-7-rpms
BuildRequires: rh-python36, rh-python36-python-virtualenv

%description
Run a program with standard output and standard error copied to files while
maintaining the original standard output and standard error as normal.

Run a program from cron, suppressing all output unless the process outputs an
error message or has a non-zero exit status whereupon the original output will
be written as normal and the exit code will be appended to standard error.

%global _hardened_build 1

%prep
%setup -q

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
source scl_source enable rh-python36
RET=$?
set -e
if [ $RET -ne 0 ]; then
	echo SCL missing
	exit 1
fi

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

if ! grep -F "op->signal_number_ = reg->signal_number_" "%{_includedir}/boost/asio/detail/impl/signal_set_service.ipp" >/dev/null; then
	mkdir -p build/redhat/boost/asio/detail/impl
	cp "%{_includedir}/boost/asio/detail/impl/signal_set_service.ipp" build/redhat/boost/asio/detail/impl/
	patch -p2 -d build/redhat < "%{_sourcedir}/749e9d221960c6703220eaf4c99b6ee913db7607.patch"
fi

PATH="$VENV_DTEE_BIN:$PATH" ninja -v -C build/redhat %{_smp_mflags}
PATH="$VENV_DTEE_BIN:$PATH" ninja -v -C build/redhat test %{_smp_mflags}

%install
PATH="$VENV_DTEE_BIN:$PATH" DESTDIR="%{buildroot}" ninja -v -C build/redhat install %{_smp_mflags}
ln -sf dtee "%{buildroot}%{_bindir}/cronty"
ln -sf dtee.1 "%{buildroot}%{_mandir}/man1/cronty.1"

%files
%license COPYING
%{_bindir}/dtee
%{_bindir}/cronty
%{_mandir}/man1/dtee.*
%{_mandir}/man1/cronty.*

%changelog
* Sun Nov 11 2018 Simon Arlott <redhat@sa.me.uk> - 0.0.0-1
- Initial release
