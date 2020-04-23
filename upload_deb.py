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
	print(f"Debian: {tag}")

	repo = tag.split("-")[0] # debian
	deb_dir = "deb/" + tag.split("/")[0] # deb/debian-9-stretch
	deb_release = tag.split("/")[0].split("-")[-1] # stretch
	deb_version = tag.split("/")[1] # 1.0.0-1
	pkg_version = src_pkg_version = deb_version.split("-")[0] # 1.0.0
	pkg_version += f"-{deb_release}-" # -stretch-
	pkg_version += deb_version.split("-")[1] # 1
	pkg_version_group = ".".join(pkg_version.split(".")[:-1]) # 1.0

	source_filename = f"source/{pkg}-{src_pkg_version}.tar.gz"
	orig_filename = f"{deb_dir}/{pkg}_{src_pkg_version}.orig.tar.gz"
	if not os.path.exists(orig_filename):
		raise FileNotFoundError(f"{orig_filename} missing")

	if stat.S_ISREG(os.lstat(orig_filename).st_mode):
		with open(source_filename, "rb") as f:
			source_data = f.read()
		with open(orig_filename, "rb") as f:
			orig_data = f.read()
		if source_data != orig_data:
			raise Exception(f"Files {source_filename} and {orig_filename} are not identical")
		print(f"  Replacing {orig_filename} with link to {source_filename}")
		os.unlink(orig_filename)
		os.link(source_filename, orig_filename)

	if deb_release == "trusty":
		deb_tar = "gz"
	else:
		deb_tar = "xz"

	if deb_release in ["stretch", "buster"]:
		ddeb = "deb"
	else:
		ddeb = "ddeb"

	files = []
	for suffix in [".dsc", f".debian.tar.{deb_tar}"]:
		files.append(("source", f"{deb_dir}/{pkg}_{deb_version}{suffix}"))

	for arch in arches:
		files.append((arch, f"{deb_dir}/{pkg}_{deb_version}_{arch}.deb"))

		if deb_release not in ["jessie", "trusty", "xenial"]:
			files.append((arch, f"{deb_dir}/{pkg}-dbgsym_{deb_version}_{arch}.{ddeb}"))

	for (arch, filename) in files:
		if not os.path.exists(filename):
			raise Exception(f"File {filename} missing")
		os.chmod(filename, stat.S_IMODE(os.stat(filename).st_mode) & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))

	bintray.create_version(org, repo, pkg, pkg_version, tag)
	for (arch, filename) in files:
		bintray.upload_file(org, repo, pkg, pkg_version, filename,
						f"pool/{deb_release}/main/{pkg}/{pkg_version_group}/{os.path.basename(filename)}",
						debian=(deb_release, "main", arch))
	bintray.publish_version(org, repo, pkg, pkg_version)
