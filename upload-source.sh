JFROG_REPO=source
TAG="$1"
JFROG_VERSION="$JFROG_ORG/$JFROG_REPO/$JFROG_PKG/$TAG"

if [ ! -e "source/"$JFROG_PKG"-$TAG.tar.gz" ]; then
	echo "Creating source $TAG"

	GIT_DIR="$JFROG_PKG".git git archive --prefix="$JFROG_PKG-$TAG/" "$TAG" > source/"$JFROG_PKG"-"$TAG".tar || exit 1
	gzip -6 -n < source/"$JFROG_PKG"-"$TAG".tar > source/"$JFROG_PKG"-"$TAG".tar.gz || exit 1
	tar -tzf source/"$JFROG_PKG"-"$TAG".tar.gz > /dev/null || exit 1
fi
chmod a-w source/"$JFROG_PKG"-"$TAG".tar.gz
rm -f "source/"$JFROG_PKG"-$TAG.tar"

jfrog bt version-show "$JFROG_VERSION" 1>.tmp1 2>.tmp2
grep -F "Bintray response: 404" .tmp2 >/dev/null
if [ $? -eq 0 ]; then
	echo "Creating version $TAG"

	TAG_TS=$(GIT_DIR="$JFROG_PKG".git git for-each-ref --format="%(creatordate:iso8601-strict)" refs/tags/"$TAG")
	TAG_DESC=$(GIT_DIR="$JFROG_PKG".git git for-each-ref --format="%(subject)" refs/tags/"$TAG")
	jfrog bt version-create --desc="$TAG_DESC" --vcs-tag="$TAG" --released="$TAG_TS" "$JFROG_VERSION" || exit 1

	jfrog bt version-show "$JFROG_VERSION" 1>.tmp1 2>.tmp2
else
	echo "Version $TAG exists"
fi

PUBLISHED=$(python3 -c 'import json, sys; print(json.load(sys.stdin)["published"])' < .tmp1)
if [ "$PUBLISHED" = "True" ]; then
	echo "Version $TAG already published"
elif [ "$PUBLISHED" = "False" ]; then
	echo "Uploading files"
	jfrog bt upload --publish source/"$JFROG_PKG"-"$TAG".tar.gz "$JFROG_VERSION" || exit 1

	echo "Publishing version"
	jfrog bt version-publish "$JFROG_VERSION" || exit 1

	firefox "https://bintray.com/artifact/showArtifactInDownloadList?versionPath=${JFROG_PKG}%2F${TAG}&pkgPath=&basePath=&artifactPath=%2F${JFROG_ORG}%2F${JFROG_REPO}%2F${JFROG_PKG}-${TAG}.tar.gz&order=asc&sort=name"
else
	echo "Version publish state \"$PUBLISHED\" unknown"
	exit 1
fi

exit 0
