.PHONY: all

all:
	rpmdev-setuptree
	spectool -g -R SPECS/dtee.spec
	QA_RPATHS=0x0002 rpmbuild -ba SPECS/dtee.spec
