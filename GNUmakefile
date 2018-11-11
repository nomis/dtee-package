.PHONY: all

all:
	rpmdev-setuptree
	spectool -g -R SPECS/dtee.spec
	rpmbuild -ba SPECS/dtee.spec
