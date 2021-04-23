# Copyright 2018,2021  Simon Arlott
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
import subprocess

from prepare_common import cp_file


def for_tag(org, pkg, tag):
	print(f"Source: {tag}")
	repo = "source"
	version = tag
	filename_tar = f"source/{pkg}-{tag}.tar"
	filename_tar_gz = f"{filename_tar}.gz"

	if not os.path.exists(filename_tar_gz):
		print("  Creating archive")
		with open(filename_tar, "wb") as f:
			subprocess.run(["git", "archive", f"--prefix={pkg}-{tag}/", tag],
				env={"GIT_DIR": f"{pkg}.git"}, stdout=f, check=True)
		subprocess.run(["gzip", "-6", "-n", filename_tar], check=True)
		subprocess.run(["tar", "-tzf", filename_tar_gz], stdout=subprocess.DEVNULL, check=True)

	if os.path.exists(filename_tar):
		os.unlink(filename_tar)

	cp_file(org, repo, filename_tar_gz, os.path.basename(filename_tar_gz))
