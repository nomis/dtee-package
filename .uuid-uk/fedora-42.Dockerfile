FROM fedora:42

RUN echo 'keepcache=True' >>/etc/dnf/dnf.conf

# A non-C locale is required for testing gettext()
RUN \
	--mount=type=cache,sharing=locked,target=/var/cache/dnf,id=fedora-42-var-cache-dnf \
	dnf install -y glibc-langpack-en langpacks-en

RUN \
	--mount=type=cache,sharing=locked,target=/var/cache/dnf,id=fedora-42-var-cache-dnf \
	dnf install -y rpm-build rpm-devel rpmlint rpmdevtools

RUN \
	--mount=type=cache,sharing=locked,target=/var/cache/dnf,id=fedora-42-var-cache-dnf \
	dnf install -y gcc gcc-c++ make meson ninja-build git procps

RUN \
	--mount=type=cache,sharing=locked,target=/var/cache/dnf,id=fedora-42-var-cache-dnf \
	dnf install -y bash coreutils diffutils patch python3-sphinx boost-devel gettext lcov

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
