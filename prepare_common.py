# Copyright 2021  Simon Arlott
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import filecmp
import os
import shutil
import stat
import subprocess


def cp_file(org, repo, src, dst):
	dst = f"uuid-bin/{org}/{repo}/{dst}"
	sig = f"{dst}.asc"

	chmod(src)
	os.makedirs(os.path.dirname(dst), exist_ok=True)

	try:
		assert filecmp.cmp(src, dst, False), [src, dst]
	except FileNotFoundError:
		os.link(src, dst)
	chmod(dst)

	if not os.path.exists(sig):
		subprocess.run(["gpg2", "--batch", "-a", "-b", "-u", "dtee.bin.uuid.uk", "-o", sig, "--", src], check=True)
	p = subprocess.run(["gpgv", "--", sig, dst], stderr=subprocess.PIPE)
	assert p.returncode == 0, [src, dst, p.stderr]

	chmod(sig)


def chmod(filename, mode=0o444):
	if stat.S_IMODE(os.lstat(filename).st_mode) != mode:
		os.chmod(filename, mode)
