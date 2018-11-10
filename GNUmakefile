.PHONY: all

URL=https://github.com/nomis/dtee

all: dtee.git
	GIT_DIR=dtee.git git fetch --tags
	bash upload-all-tags.sh

dtee.git:
	git clone --bare "$(URL)" "$@"
