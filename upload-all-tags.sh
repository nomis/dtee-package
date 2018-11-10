export JFROG_CLI_OFFER_CONFIG=false
export JFROG_ORG=dtee
export JFROG_PKG=dtee

while read -r tag; do
	bash upload-source.sh "$tag" </dev/null || exit 1
	#bash upload-deb.sh "$tag" </dev/null || exit 1
	#bash upload-rpm.sh "$tag" </dev/null || exit 1
done < <(cd dtee.git && git tag | sort -n -r)

echo OK
