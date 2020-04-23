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

import json
import os
import requests
import subprocess
import yaml
import hashlib
import time


API_URL = "https://bintray.com/api/v1"

__VERSIONS = set()
__PUBLISHED = set()
__FILES = {}

with open("credentials.yaml", "rt") as f:
	__CREDENTIALS = yaml.load(f)


def __api_request(method, path, **kwargs):
	result = requests.request(method, f"{API_URL}{path}", auth=(__CREDENTIALS["user"], __CREDENTIALS["key"]), **kwargs)
	if result.status_code < 200 or (result.status_code >= 300 and result.status_code < 400) or result.status_code >= 500:
		raise Exception(f"API response for {method} {path}: {result.status_code} {repr(result.headers)} ({repr(result.content)})")
	try:
		return (result.status_code < 400, result.status_code, json.loads(result.content) if result.content else None)
	except json.decoder.JSONDecodeError:
		raise Exception(f"API response for {method} {path}: {result.status_code} {repr(result.headers)} ({repr(result.content)})")

def __version_exists(org, repo, pkg, version):
	path = f"{org}/{repo}/{pkg}/{version}"
	if path not in __VERSIONS:
		print(f"  Bintray <= Query version {version}")
		(success, code, data) = __api_request("GET", f"/packages/{org}/{repo}/{pkg}/versions/{version}")
		if success:
			__VERSIONS.add(path)
			if data["published"]:
				__PUBLISHED.add(path)
	return path in __VERSIONS

def __version_create(org, repo, pkg, version, tag, ts, desc):
	path = f"{org}/{repo}/{pkg}/{version}"
	print(f"  Bintray => Create version {version} released at {ts}")
	(success, code, data) = __api_request("POST", f"/packages/{org}/{repo}/{pkg}/versions", data=json.dumps({
			"name": version,
			"vcs_tag": tag,
			"released": ts,
			"desc": desc,
			"published": False,
		}))
	if success:
		__VERSIONS.add(path)
	else:
		raise Exception(f"Unable to create version: {code} ({repr(data)})")

def __version_published(org, repo, pkg, version):
	if not __version_exists(org, repo, pkg, version):
		return False

	path = f"{org}/{repo}/{pkg}/{version}"
	return path in __PUBLISHED

def __version_publish(org, repo, pkg, version):
	path = f"{org}/{repo}/{pkg}/{version}"
	print(f"  Bintray => Publish version {version}")
	(success, code, data) = __api_request("PATCH", f"/packages/{org}/{repo}/{pkg}/versions/{version}", data=json.dumps({ "published": True }))
	if success:
		__PUBLISHED.add(path)
	else:
		raise Exception(f"Unable to publish version: {code} ({repr(data)})")

def __file_exists(org, repo, pkg, version, source, target):
	if (org, repo, version) not in __FILES:
		print(f"  Bintray <= List files for version {version}")
		(success, code, data) = __api_request("GET", f"/packages/{org}/{repo}/{pkg}/versions/{version}/files?include_unpublished=1")
		if success:
			__FILES[(org, repo, version)] = dict((file["path"], (file["size"], file["sha256"])) for file in data)
		else:
			raise Exception(f"Unable to list files: {code} ({repr(data)})")

	if target in __FILES[(org, repo, version)]:
		local_size = os.stat(source).st_size
		with open(source, "rb") as f:
			m = hashlib.sha256()
			m.update(f.read())
			local_hash = m.hexdigest()
		(remote_size, remote_hash) = __FILES[(org, repo, version)][target]
		if local_size != remote_size:
			raise Exception(f"File size mismatch for {target} {remote_size} != {local_size} ({source})")
		if local_hash != remote_hash:
			raise Exception(f"File hash mismatch for {target} {remote_hash} != {local_hash} ({source})")
		return True
	return False

def __file_upload(org, repo, pkg, version, source, target, debian=None):
	path = f"{org}/{repo}/{pkg}/{version}"
	with open(source, "rb") as f:
		content = f.read()
	m = hashlib.sha256()
	m.update(content)
	local_hash = m.hexdigest()
	if debian is not None:
		print(f"  Bintray => Upload file {target} for {debian}")
		(success, code, data) = __api_request("PUT",
			f"/content/{org}/{repo}/{pkg}/{version}/{target};deb_distribution={debian[0]};deb_component={debian[1]};deb_architecture={debian[2]}?publish=1",
			data=content, headers={ "X-Checksum-Sha2": local_hash })
	else:
		print(f"  Bintray => Upload file {target}")
		(success, code, data) = __api_request("PUT",
			f"/content/{org}/{repo}/{pkg}/{version}/{target}?publish=1",
			data=content, headers={ "X-Checksum-Sha2": local_hash })
	if success:
		__FILES[(org, repo, target)] = (os.stat(source).st_size, local_hash)
	else:
		raise Exception(f"Unable to upload file: {code} ({repr(data)})")


def create_version(org, repo, pkg, version, tag):
	if not __version_exists(org, repo, pkg, version):
		source = True
		ts = subprocess.run(["git", "for-each-ref", "--format=%(creatordate:iso8601-strict)", f"refs/tags/{tag}"],
				env={ "GIT_DIR": f"{pkg}.git" }, stdout=subprocess.PIPE, check=True, universal_newlines=True).stdout.strip()
		if not ts:
			ts = subprocess.run(["git", "for-each-ref", "--format=%(creatordate:iso8601-strict)", f"refs/tags/{tag}"],
					stdout=subprocess.PIPE, check=True, universal_newlines=True).stdout.strip()
			source = False
		assert ts, f"No timestamp for tag {tag}"
		desc = subprocess.run(["git", "for-each-ref", "--format=%(subject)", f"refs/tags/{tag}"],
				env={ "GIT_DIR": f"{pkg}.git" }, stdout=subprocess.PIPE, check=True, universal_newlines=True).stdout.strip()
		if source and not desc:
			assert ts, f"No description for tag {tag}"
		__version_create(org, repo, pkg, version, tag, ts, desc)
	else:
		print(f"  Bintray -- Version {version} already exists")

def publish_version(org, repo, pkg, version):
	if not __version_published(org, repo, pkg, version):
		time.sleep(3)
		__version_publish(org, repo, pkg, version)
	else:
		print(f"  Bintray -- Version {version} already published")

def upload_file(org, repo, pkg, version, source, target, debian=None):
	if not __file_exists(org, repo, pkg, version, source, target):
		__file_upload(org, repo, pkg, version, source, target, debian)
	else:
		print(f"  Bintray -- File {target} already exists")

def calc_metadata(org, repo, path=""):
	print(f"  Bintray => Calculate metadata for {org}/{repo}/{path}")
	(success, code, data) = __api_request("POST", f"/calc_metadata/{org}/{repo}/{path}")
	if not success:
		raise Exception(f"Unable to recalculate metadata: {code} ({repr(data)})")
