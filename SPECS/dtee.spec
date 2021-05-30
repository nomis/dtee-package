Name:    dtee
Version: 1.1.0
Release: 1%{?dist}
Summary: Run a program with standard output and standard error copied to files

License: GPLv3+
URL:     https://dtee.readthedocs.io/
Source0: https://dtee.bin.uuid.uk/source/%{name}-%{version}.tar.gz

BuildRequires: glibc, make, gcc, gcc-c++, boost-devel
BuildRequires: bash, coreutils, diffutils, findutils, grep
BuildRequires: python3-virtualenv

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

virtualenv build/virtualenv/dtee
build/virtualenv/dtee/bin/python3 build/virtualenv/dtee/bin/pip install \
	--upgrade pip==8.1.1 --no-deps --ignore-installed
build/virtualenv/dtee/bin/python3 build/virtualenv/dtee/bin/pip install \
	meson==0.53.2 \
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
VENV_DTEE_BIN="$PWD/build/virtualenv/dtee/bin"
PATH="$VENV_DTEE_BIN:$PATH" \
	CFLAGS="$RPM_OPT_FLAGS" \
	CXXFLAGS="$RPM_OPT_FLAGS" \
	LDFLAGS="$RPM_LD_FLAGS" \
	meson \
	--prefix "%{_prefix}" \
	--bindir "%{_bindir}" \
	--mandir "%{_mandir}" \
	--datadir "%{_datadir}" \
	--buildtype=plain \
	--unity on \
	build/redhat

PATH="$VENV_DTEE_BIN:$PATH" ninja -v -C build/redhat %{_smp_mflags}
PATH="$VENV_DTEE_BIN:$PATH" ninja -v -C build/redhat test %{_smp_mflags}

%install
VENV_DTEE_BIN="$PWD/build/virtualenv/dtee/bin"
PATH="$VENV_DTEE_BIN:$PATH" DESTDIR="%{buildroot}" ninja -v -C build/redhat install %{_smp_mflags}
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
