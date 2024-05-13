FROM ubuntu:jammy
ENV DEBIAN_FRONTEND=noninteractive

RUN rm /etc/apt/apt.conf.d/docker-clean
RUN echo 'APT::Keep-Downloaded-Packages "true";' >/etc/apt/apt.conf.d/keep-downloaded-packages

RUN \
	--mount=type=cache,sharing=locked,target=/var/cache/apt,id=ubuntu-jammy-var-cache-apt \
	--mount=type=cache,sharing=locked,target=/var/lib/apt,id=ubuntu-jammy-var-lib-apt \
	apt-get update
RUN \
	--mount=type=cache,sharing=locked,target=/var/cache/apt,id=ubuntu-jammy-var-cache-apt \
	--mount=type=cache,sharing=locked,target=/var/lib/apt,id=ubuntu-jammy-var-lib-apt \
	apt-get install -y build-essential git procps python3-pip
RUN \
	--mount=type=cache,sharing=locked,target=/var/cache/apt,id=ubuntu-jammy-var-cache-apt \
	--mount=type=cache,sharing=locked,target=/var/lib/apt,id=ubuntu-jammy-var-lib-apt \
	apt-get install -y libboost-all-dev gettext lcov

# A non-C locale is required for testing gettext()
RUN \
	--mount=type=cache,sharing=locked,target=/var/cache/apt,id=ubuntu-jammy-var-cache-apt \
	--mount=type=cache,sharing=locked,target=/var/lib/apt,id=ubuntu-jammy-var-lib-apt \
	apt-get install -y locales

RUN sed -E 's/^# (en_AU.+ UTF-8)$/\1/' -i /etc/locale.gen
RUN locale-gen

RUN \
	--mount=type=cache,sharing=locked,target=/var/cache/apt,id=ubuntu-jammy-var-cache-apt \
	--mount=type=cache,sharing=locked,target=/var/lib/apt,id=ubuntu-jammy-var-lib-apt \
	apt-get install -y wget debhelper meson ninja-build python3-sphinx

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
	/bin/dash -pc "groupadd -g \$(id -rg) user" || exit 1
	/bin/dash -pc "useradd -u \$(id -ru) -g \$(id -rg) -d /home/user -s /bin/bash user" || exit 1
	/bin/dash -pc "install -d -m 0700 -o user -g user /home/user" || exit 1
	/bin/dash -pc "chmod u-s /bin/dash" || exit 1
fi
exec "\$@"
EOT
	chmod +x /entrypoint.sh
EOF

HEALTHCHECK --start-period=1s --start-interval=1s --retries=1 CMD [ ! -u /bin/dash ]
ENTRYPOINT ["/entrypoint.sh"]
