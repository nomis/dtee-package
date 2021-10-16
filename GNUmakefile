.PHONY: all www supported metadata

URL=https://github.com/nomis/dtee

all: dtee.git
	GIT_DIR=dtee.git git fetch --prune --tags
	python3 prepare_all_tags.py

dtee.git:
	git clone --bare "$(URL)" "$@"

www:
	find source/ deb/ rpm/ -type f -not -name .gitignore -not -name '*.sig' -exec ./sign.sh {} \;
	find source/ deb/ rpm/ -type f -not -name .gitignore -not -perm 0444 -exec chmod 444 {} \;
	rsync -ai source/ skund:dtee-s85-org/source/ --exclude=.gitignore
	rsync -ai deb/ skund:dtee-s85-org/deb/ --exclude=.gitignore
	rsync -ai rpm/ skund:dtee-s85-org/rpm/ --exclude=.gitignore
	rsync -rlptDHi --delete --delete-after --exclude=.snapshots/ uuid-bin/dtee/.htaccess uuid-bin/dtee/* chalk:dtee-bin-uuid-uk/
	rsync -rlptDHi --delete --delete-after --exclude=.snapshots/ uuid-bin/dtee/.htaccess uuid-bin/dtee/* djelibeybi:dtee-bin-uuid-uk/
	rsync -rlptDHi --delete --delete-after --exclude=.snapshots/ uuid-bin/dtee/.htaccess uuid-bin/dtee/* genua:dtee-bin-uuid-uk/
	rsync -rlptDHi --delete --delete-after --exclude=.snapshots/ uuid-bin/dtee/.htaccess uuid-bin/dtee/* papylos:dtee-bin-uuid-uk/
	rsync -rlptDHi --delete --delete-after --exclude=.snapshots/ uuid-bin/dtee/.htaccess uuid-bin/dtee/* quirm:dtee-bin-uuid-uk/
	rsync -rlptDHi --delete --delete-after --exclude=.snapshots/ uuid-bin/dtee/.htaccess uuid-bin/dtee/* skund:dtee-bin-uuid-uk/

supported:
	xdg-open https://wiki.debian.org/LTS
	xdg-open https://wiki.ubuntu.com/Releases
	xdg-open https://access.redhat.com/support/policy/updates/errata/#Life_Cycle_Dates
	xdg-open https://en.wikipedia.org/wiki/Fedora_version_history#Version_history
