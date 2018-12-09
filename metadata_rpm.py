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

import requests

import bintray


def __get(url):
	print(f"Bintray: <= {url}")
	result = requests.request("GET", url)
	success = result.status_code >= 200 and result.status_code < 300
	if not success:
		print(f"  {url} missing")
	return (success, result.content)


def for_tags(org, pkg, tags, arches):
	for repo in list(dict.fromkeys([tag.split("/")[0].split("-")[0] for tag in tags])):
		for release in list(dict.fromkeys([tuple(tag.split("/")[0].split("-")) for tag in list(
					filter(lambda tag: tag.split("/")[0].split("-")[0] == repo, tags))]
				)):
			for arch in arches:
				ok = for_versions(org, pkg, release[0], release[1], arch,		
						[tag.split("/")[1] for tag in list(
							filter(lambda tag: tuple(tag.split("/")[0].split("-")) == release, tags))]
					)
				print(f"RedHat: Metadata for {org}/{repo} ({release[1]}/{arch}) {'exists' if ok else 'is missing'}")
				if not ok:
					bintray.calc_metadata(org, repo, f"{release}/{arch}")
					pass
	
def for_versions(org, pkg, repo, release, arch, exp_versions):
	ok = True
		
	(success, data) = __get(f"https://dl.bintray.com/{org}/{repo}/{release}/{arch}/repodata/repomd.xml.asc")
	ok = ok and success
	(success, data) = __get(f"https://dl.bintray.com/{org}/{repo}/{release}/{arch}/repodata/repomd.xml")
	ok = ok and success
	
	# TODO parse XML and check versions

	return ok
