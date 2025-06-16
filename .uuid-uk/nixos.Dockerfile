FROM nixos/nix:latest

# Jenkins always runs commands in the container as its own UID/GID, which has no
# access to anything outside the container. It also does this for the entrypoint
# so a setuid executable is required for this hack.
#
# This file should not have a fixed UID/GID for Jenkins so determine the UID/GID
# at runtime when executing the entrypoint and use the setuid shell to set up
# a user and fix filesystem permissions on startup.
#
# Start a nix-daemon as root so that nix-shell as the user works. This requires
# python3 to elevate from euid=0 to uid=0.
RUN mkdir -p /usr/local/docker

RUN <<EOF
	cat >/usr/local/docker/setup.sh <<EOT
#!/bin/sh
cp "\$(which dash)" /usr/local/docker/dash
ln -s "\$(which python3)" /usr/local/docker/python3
EOT
	chmod +x /usr/local/docker/setup.sh

	cat >/usr/local/docker/nix-daemon.py <<EOT
#!/usr/local/docker/python3
import os
os.setreuid(0, 0)
os.setregid(0, 0)
os.setgroups([0])
os.system('nix-shell -p nix --run "nix-daemon --daemon"')
EOT
	chmod +x /usr/local/docker/nix-daemon.py
EOF

RUN nix-shell -p dash nix python3 --run /usr/local/docker/setup.sh

RUN chmod u+s /usr/local/docker/dash

RUN <<EOF
	cat >/usr/local/docker/entrypoint.sh <<EOT
#!/usr/local/docker/dash
if [ -u /usr/local/docker/dash ]; then
	echo "user:x:\$(id -rg):user" | /usr/local/docker/dash -c "tee -a /etc/group" || exit 1
	echo "user:x:\$(id -ru):\$(id -rg)::/home/user:/bin/sh" | /usr/local/docker/dash -c "tee -a /etc/passwd" || exit 1
	/usr/local/docker/dash -c "install -d -m 0700 -o user -g user /home/user" || exit 1
	/usr/local/docker/dash -c "install -d -m 0755 -o user -g user /nix/var/nix/profiles/per-user/user" || exit 1
	/usr/local/docker/dash -c "install -d -m 0755 -o user -g user /nix/var/nix/gcroots/per-user/user" || exit 1
	/usr/local/docker/dash -c "/usr/local/docker/nix-daemon.py" </dev/null 1>/dev/null 2>/dev/null &
	/usr/local/docker/dash -c "chmod u-s /usr/local/docker/dash" || exit 1
fi
exec "\$@"
EOT
	chmod +x /usr/local/docker/entrypoint.sh
EOF

HEALTHCHECK --start-period=1s --start-interval=1s --retries=1 CMD [ ! -u /usr/local/docker/dash ]
ENTRYPOINT ["/usr/local/docker/entrypoint.sh"]
