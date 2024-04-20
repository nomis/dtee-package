# Copyright 2018,2020-2021,2023-2024  Simon Arlott
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

import glob
import os
import stat
import subprocess

from prepare_common import cp_file, chmod


def for_tag(org, pkg, tag, arches):
	print(f"RedHat: {tag}")

	rpm_dir = "rpm/" + tag.split("/")[0].split("_")[0] # rpm/rhel-7
	(rpm_distro, rpm_fullrelease) = tag.split("/")[0].split("-") # rhel, 7_9
	rpm_release = rpm_fullrelease.split("_")[0] # 7
	rpm_version = tag.split("/")[1] # 1.0.0-1
	pkg_version = rpm_version.split("-")[0] # 1.0.0
	pkg_version += f"-{rpm_release}-" # -7-
	pkg_version += rpm_version.split("-")[1] # 1
	pkg_version_group = ".".join(pkg_version.split(".")[:-1]) # 1.0

	rpm_map = {
		"rhel": ("redhat", f"el{rpm_fullrelease}"),
		"fedora": ("fedora", f"fc{rpm_fullrelease}"),
	}
	(repo, rpm_id) = rpm_map[rpm_distro]

	if rpm_distro == "rhel" and int(rpm_release) < 8:
		variants = ["", "-debuginfo"]
	else:
		variants = ["", "-debuginfo", "-debugsource"]

	files = []
	files.append(("source", f"{rpm_dir}/{pkg}-{rpm_version}.{rpm_id}.src.rpm"))

	for arch in arches:
		for variant in variants:
			files.append((arch, f"{rpm_dir}/{pkg}{variant}-{rpm_version}.{rpm_id}.{arch}.rpm"))

	for (arch, filename) in files:
		if not os.path.exists(filename):
			raise Exception(f"File {filename} missing")
		chmod(filename, stat.S_IMODE(os.stat(filename).st_mode) & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))

	for (arch, filename) in files:
		cp_file(org, repo, filename, f"{rpm_release}/{arch}/{pkg}/{pkg_version_group}/{os.path.basename(filename)}")


def for_repos(org, repo):
	root = f"uuid-bin/{org}/{repo}"
	for dir in sorted(glob.glob(f"{root}/*/*")):
		repomd = f"{dir}/repodata/repomd.xml"
		sig = repomd + ".asc"

		changed = False
		if os.path.exists(repomd):
			timestamp = 0
			for file in glob.glob(f"{dir}/*/*/*.rpm"):
				timestamp = max(timestamp, os.path.getctime(file))

			if timestamp >= os.path.getctime(repomd):
				changed = True
		else:
			changed = True

		if changed:
			prev = None
			try:
				with open(repomd, "rb") as f:
					prev = f.read()
			except FileNotFoundError:
				pass

			subprocess.run(["createrepo_c", "--no-database", "-s", "sha256", "--compress-type=gz", "--update", "--retain-old-md=0", dir], check=True)

			with open(repomd, "rb") as f:
				curr = f.read()

			if prev != curr:
				try:
					os.unlink(sig)
				except FileNotFoundError:
					pass

		if not os.path.exists(sig):
			subprocess.run(["gpg2", "--batch", "-a", "-b", "-u", "dtee.bin.uuid.uk", "-o", sig, "--", repomd], check=True)
		p = subprocess.run(["gpgv", "--", sig, repomd], stderr=subprocess.PIPE)
		assert p.returncode == 0, [repomd, sig, p.stderr]
		chmod(sig)

		akey = repomd + ".key"
		if not os.path.exists(akey):
			subprocess.run(["gpg2", "-a", "-o", akey, "--export", "dtee.bin.uuid.uk"], check=True)
		chmod(akey)
