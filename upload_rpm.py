# Copyright 2018,2020  Simon Arlott
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

import stat
import os

import bintray


def for_tag(org, pkg, tag, arches):
	print(f"RedHat: {tag}")

	rpm_dir = "rpm/" + tag.split("/")[0] # rpm/rhel-7
	(rpm_distro, rpm_release) = tag.split("/")[0].split("-") # rhel, 7
	rpm_version = tag.split("/")[1] # 1.0.0-1
	pkg_version = rpm_version.split("-")[0] # 1.0.0
	pkg_version += f"-{rpm_release}-" # -7-
	pkg_version += rpm_version.split("-")[1] # 1
	pkg_version_group = ".".join(pkg_version.split(".")[:-1]) # 1.0

	rpm_map = {
		"rhel": ("redhat", f"el{rpm_release}"),
		"fedora": ("fedora", f"fc{rpm_release}"),
	}
	(repo, rpm_id) = rpm_map[rpm_distro]

	if rpm_distro == "rhel":
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
		os.chmod(filename, stat.S_IMODE(os.stat(filename).st_mode) & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))

	bintray.create_version(org, repo, pkg, pkg_version, tag)
	for (arch, filename) in files:
		bintray.upload_file(org, repo, pkg, pkg_version, filename,
						f"{rpm_release}/{arch}/{pkg}/{pkg_version_group}/{os.path.basename(filename)}")
	bintray.publish_version(org, repo, pkg, pkg_version)
