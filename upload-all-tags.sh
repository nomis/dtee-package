export JFROG_CLI_OFFER_CONFIG=false
export JFROG_ORG=dtee
export JFROG_PKG=dtee

while read -r tag; do
	echo
	echo "Source: $tag"
	bash upload-source.sh "$tag" </dev/null || exit 1
done < <(GIT_DIR=dtee.git git tag | sort -n)

while read -r tag; do
	echo
	echo "Debian: $tag"
	bash upload-deb.sh "$tag" amd64 </dev/null || exit 1
done < <(git tag | grep -E -e ^debian- -e ^ubuntu- | sort -n)

while read -r tag; do
	echo
	echo "RedHat: $tag"
	bash upload-rpm.sh "$tag" x86_64 </dev/null || exit 1
done < <(git tag | grep -E -e ^rhel- -e ^fedora- | sort -n)

echo
echo OK
