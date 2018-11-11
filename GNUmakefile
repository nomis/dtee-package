.PHONY: all

all:
	ln -sf "$(PWD)/SPECS/dtee.spec" "$(HOME)/rpmbuild/SPECS/dtee.spec"
	ln -sf "$(PWD)/SOURCES/749e9d221960c6703220eaf4c99b6ee913db7607.patch" "$(HOME)/rpmbuild/SOURCES/749e9d221960c6703220eaf4c99b6ee913db7607.patch"
	rpmbuild -ba "$(HOME)/rpmbuild/SPECS/dtee.spec"
