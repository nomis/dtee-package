# Copyright 2018,2020-2021  Simon Arlott
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

import email.utils
import filecmp
import hashlib
import glob
import os
import stat
import subprocess

from prepare_common import cp_file, chmod


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

	if os.lstat(source_filename) != os.lstat(orig_filename):
		if not filecmp.cmp(source_filename, orig_filename, False):
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
	files.append(("source", orig_filename))
	for suffix in [".dsc", f".debian.tar.{deb_tar}"]:
		files.append(("source", f"{deb_dir}/{pkg}_{deb_version}{suffix}"))

	for arch in arches:
		files.append((arch, f"{deb_dir}/{pkg}_{deb_version}_{arch}.deb"))

		if deb_release not in ["jessie", "trusty", "xenial"]:
			files.append((arch, f"{deb_dir}/{pkg}-dbgsym_{deb_version}_{arch}.{ddeb}"))

	for (arch, filename) in files:
		if not os.path.exists(filename):
			raise Exception(f"File {filename} missing")
		chmod(filename, stat.S_IMODE(os.stat(filename).st_mode) & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))

	for (arch, filename) in files:
		dst_filename = f"pool/{deb_release}/main/{pkg}/{pkg_version_group}/{os.path.basename(filename)}"
		if dst_filename.endswith(".ddeb"):
			dst_filename = dst_filename[:-5] + ".deb"
		cp_file(org, repo, filename, dst_filename)


def for_repos(org, repo):
	root = f"uuid-bin/{org}/{repo}"
	comp = [
		(".gz", ["gzip", "-9", "-k"]),
		(".bz2", ["bzip2", "-9", "-k"]),
		(".xz", ["xz", "-9", "-k"]),
	]
	now =  email.utils.formatdate(timeval=None, localtime=False, usegmt=True)

	bkey = f"{root}/repo-key.gpg"
	akey = f"{root}/repo-key.asc"
	if not os.path.exists(bkey):
		subprocess.run(["gpg2", "-o", bkey, "--export", "dtee.bin.uuid.uk"], check=True)
	chmod(bkey)
	if not os.path.exists(akey):
		subprocess.run(["gpg2", "-a", "-o", akey, "--export", "dtee.bin.uuid.uk"], check=True)
	chmod(akey)

	for pool in glob.glob(f"{root}/pool/*"):
		name = os.path.basename(pool)

		files = []
		arches = ["amd64", "i386"]
		for arch in arches:
			packages = subprocess.run(["dpkg-scanpackages", "-a", arch, "-m", f"pool/{name}"], cwd=root, stdout=subprocess.PIPE, encoding="UTF-8", check=True).stdout
			packages_filename = f"{root}/dists/{name}/main/binary-{arch}/Packages"

			os.makedirs(os.path.dirname(packages_filename), exist_ok=True)
			output = False
			if os.path.exists(packages_filename):
				with open(packages_filename, "rt") as f:
					if f.read() != packages:
						output = True

				for cext, _ in comp:
					if not os.path.exists(packages_filename + cext):
						output = True
			else:
				output = True

			if output:
				try:
					os.unlink(packages_filename)
				except FileNotFoundError:
					pass

				for cext, _ in comp:
					try:
						os.unlink(packages_filename + cext)
					except FileNotFoundError:
						pass

				with open(packages_filename, "wt") as f:
					f.write(packages)

				for _, ccmd in comp:
					subprocess.run(ccmd + ["--", packages_filename], check=True)

			chmod(packages_filename)
			for _, ccmd in comp:
				chmod(packages_filename + cext)

			files.append(os.path.relpath(packages_filename, root))
			for cext, _ in comp:
				files.append(os.path.relpath(packages_filename + cext, root))

		sources = subprocess.run(["dpkg-scansources", f"pool/{name}"], cwd=root, stdout=subprocess.PIPE, encoding="UTF-8", check=True).stdout
		sources_filename = f"{root}/dists/{name}/main/source/Sources"

		os.makedirs(os.path.dirname(sources_filename), exist_ok=True)
		output = False
		if os.path.exists(sources_filename):
			with open(sources_filename, "rt") as f:
				if f.read() != sources:
					output = True

			for cext, _ in comp:
				if not os.path.exists(sources_filename + cext):
					output = True
		else:
			output = True

		if output:
			try:
				os.unlink(sources_filename)
			except FileNotFoundError:
				pass

			for cext, _ in comp:
				try:
					os.unlink(sources_filename + cext)
				except FileNotFoundError:
					pass

			with open(sources_filename, "wt") as f:
				f.write(sources)

			for _, ccmd in comp:
				subprocess.run(ccmd + ["--", sources_filename], check=True)

		chmod(sources_filename)
		for _, ccmd in comp:
			chmod(sources_filename + cext)

		files.append(os.path.relpath(sources_filename, root))
		for cext, _ in comp:
			files.append(os.path.relpath(sources_filename, root) + cext)

		release = f"""Origin: {org}.bin.uuid.uk
Label: {org}
Suite: {name}
Codename: {name}
Date: {now}
Components: main
Architectures: {" ".join(arches)}
"""

		for atext, aname in [("MD5Sum", "md5"), ("SHA1", "sha1"), ("SHA256", "sha256"), ("SHA512", "sha512")]:
			release += f"{atext}:\n"
			for file in files:
				with open(f"{root}/{file}", "rb") as f:
					data = f.read()
					hash = hashlib.new(aname)
					hash.update(data)
					hash = hash.hexdigest()
					relfile = os.path.relpath(f"{root}/{file}", f"{root}/dists/{name}")
					release += f" {hash} {len(data): >16} {relfile}\n"

		release_filename = f"{root}/dists/{name}/Release"
		release_sig_filename = release_filename + ".gpg"
		inrelease_filename = f"{root}/dists/{name}/InRelease"
		output = False
		if os.path.exists(release_filename):
			with open(release_filename, "rt") as f:
				data = list(filter(lambda x: not x.startswith("Date: "), f.read().splitlines()))
				release_nodate = list(filter(lambda x: not x.startswith("Date: "), release.splitlines()))

				if data != release_nodate:
					output = True
		else:
			output = True

		if output:
			try:
				os.unlink(release_filename)
			except FileNotFoundError:
				pass

			try:
				os.unlink(release_filename + ".gpg")
			except FileNotFoundError:
				pass

			try:
				os.unlink(inrelease_filename)
			except FileNotFoundError:
				pass

			with open(release_filename, "wt") as f:
				f.write(release)
			chmod(release_filename)

		if not os.path.exists(release_sig_filename):
			subprocess.run(["gpg2", "--batch", "-b", "-u", "dtee.bin.uuid.uk", "-o", release_sig_filename, "--", release_filename], check=True)
		p = subprocess.run(["gpgv", "--", release_sig_filename, release_filename], stderr=subprocess.PIPE)
		assert p.returncode == 0, [release_filename, release_sig_filename, p.stderr]
		chmod(release_sig_filename)

		if not os.path.exists(inrelease_filename):
			subprocess.run(["gpg2", "--batch", "--clear-sign", "-u", "dtee.bin.uuid.uk", "-o", inrelease_filename, "--", release_filename], check=True)
			p = subprocess.run(["gpgv", "--", inrelease_filename], stderr=subprocess.PIPE)
		assert p.returncode == 0, [release_filename, release_sig_filename, p.stderr]
		chmod(inrelease_filename)

