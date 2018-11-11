.PHONY: all

all:
	rpmdev-setuptree
	spectool -g -R SPECS/dtee.spec
	ln -sf "$(PWD)/SPECS/dtee.spec" "$(HOME)/rpmbuild/SPECS/dtee.spec"
	rpmbuild -ba "$(HOME)/rpmbuild/SPECS/dtee.spec"
