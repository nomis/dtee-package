# Copyright 2018  Simon Arlott
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

import subprocess

import upload_source
import upload_deb
import upload_rpm


def source_tags(pkg):
	return subprocess.run(["git", "tag"],
		env={ "GIT_DIR": f"{pkg}.git" },
		stdout=subprocess.PIPE,
		check=True,
		universal_newlines=True).stdout.rstrip().split("\n")

def package_tags(prefixes=None):
	all_tags = subprocess.run(["git", "tag"],
		stdout=subprocess.PIPE,
		check=True,
		universal_newlines=True).stdout.rstrip().split("\n")

	if prefixes is None:
		return all_tags

	def filter_tags(tag):
		return any([tag.startswith(prefix) for prefix in prefixes])

	return list(filter(filter_tags, all_tags))


if __name__ == "__main__":
	org = "dtee"
	pkg = "dtee"

	for tag in source_tags(pkg):
		upload_source.for_tag(org, pkg, tag)

	for tag in package_tags(["debian-", "ubuntu-"]):
		upload_deb.for_tag(org, pkg, tag, ["amd64"])

	for tag in package_tags(["rhel-", "fedora-"]):
		upload_rpm.for_tag(org, pkg, tag, ["x86_64"])
