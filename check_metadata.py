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

import bintray
import metadata_deb
import metadata_rpm
import upload_all_tags


if __name__ == "__main__":
	org = "dtee"
	pkg = "dtee"
	
	metadata_deb.for_tags(org, pkg, upload_all_tags.package_tags(["debian-", "ubuntu-"]), ["amd64"])
	metadata_rpm.for_tags(org, pkg, upload_all_tags.package_tags(["redhat-", "fedora-"]), ["source", "x86_64"])
