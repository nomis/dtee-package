.PHONY: all www

URL=https://github.com/nomis/dtee

all: dtee.git
	GIT_DIR=dtee.git git fetch --tags
	bash upload-all-tags.sh

dtee.git:
	git clone --bare "$(URL)" "$@"

www:
	find source/ deb/ rpm/ -type f -not -name .gitignore -exec chmod a-w {} \;
	rsync -ai source/ skund:dtee-s85-org/source/ --exclude=.gitignore
	rsync -ai deb/ skund:dtee-s85-org/deb/ --exclude=.gitignore
	rsync -ai rpm/ skund:dtee-s85-org/rpm/ --exclude=.gitignore
