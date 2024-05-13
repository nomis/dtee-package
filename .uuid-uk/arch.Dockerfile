FROM archlinux:base-devel

RUN pacman --noconfirm -Syu \
	dash glibc-locales git gnupg

RUN pacman --noconfirm -Syu \
	boost-libs libboost_program_options.so \
	boost meson ninja python-sphinx \
	bash coreutils diffutils findutils

# Jenkins always runs commands in the container as its own UID/GID, which has no
# access to anything outside the container. It also does this for the entrypoint
# so a setuid executable is required for this hack.
#
# This file should not have a fixed UID/GID for Jenkins so determine the UID/GID
# at runtime when executing the entrypoint and use the setuid shell to set up
# a user and fix filesystem permissions on startup. We can't use sudo (which is
# just extra overhead) because that requires an entry in /etc/passwd.
RUN chmod u+s /bin/dash
RUN <<EOF
	cat >/entrypoint.sh <<EOT
#!/bin/dash
if [ -u /bin/dash ]; then
	/bin/dash -c "groupadd -g \$(id -rg) user" || exit 1
	/bin/dash -c "useradd -u \$(id -ru) -g \$(id -rg) -d /home/user -s /bin/bash user" || exit 1
	/bin/dash -c "install -d -m 0700 -o user -g user /home/user" || exit 1
	/bin/dash -c "chmod u-s /bin/dash" || exit 1
fi
exec "\$@"
EOT
	chmod +x /entrypoint.sh
EOF

HEALTHCHECK --start-period=1s --start-interval=1s --retries=1 CMD [ ! -u /bin/dash ]
ENTRYPOINT ["/entrypoint.sh"]
