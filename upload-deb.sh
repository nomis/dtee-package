TAG="$1"
ARCHES="$2"
DEB_DIR="${TAG%%/*}"
DEB_RELEASE="${DEB_DIR##*-}"
DEB_VER="${TAG##*/}"
PKG_VER="${DEB_VER%%-*}"
JFROG_REPO="${TAG%%-*}"
JFROG_VERSION="$JFROG_ORG/$JFROG_REPO/$JFROG_PKG/$PKG_VER"

filename="deb/$DEB_DIR/${JFROG_PKG}_$PKG_VER.orig.tar.gz"
if [ ! -e "$filename" ]; then
	echo "$filename missing"
	exit 1
fi
cmp "$filename" "source/$JFROG_PKG-$PKG_VER.tar.gz" || exit 1
if [ ! -h "$filename" ]; then
	ln -sf "../../source/$JFROG_PKG-$PKG_VER.tar.gz" "deb/$DEB_DIR/${JFROG_PKG}_$PKG_VER.orig.tar.gz" || exit 1
fi
chmod a-w "$filename"

for file in .dsc .debian.tar.xz; do
	filename="deb/$DEB_DIR/${JFROG_PKG}_$DEB_VER$file"
	if [ ! -e "$filename" ]; then
		echo "$filename missing"
		exit 1
	fi
	chmod a-w "$filename"
done

case "$DEB_RELEASE" in
	stretch) DDEB=deb ;;
	*) DDEB=ddeb ;;
esac

for arch in $ARCHES; do
	filename="deb/$DEB_DIR/${JFROG_PKG}_${DEB_VER}_$arch.deb"
	if [ ! -e "$filename" ]; then
		echo "$filename missing"
		exit 1
	fi
	chmod a-w "$filename"

	if [ "$DEB_RELEASE" != "jessie" ] && [ "$DEB_RELEASE" != "xenial" ]; then
		filename="deb/$DEB_DIR/$JFROG_PKG-dbgsym_${DEB_VER}_$arch.$DDEB"
		if [ ! -e "$filename" ]; then
			echo "$filename missing"
			exit 1
		fi
		chmod a-w "$filename"
	fi
done

jfrog bt version-show "$JFROG_VERSION" 1>.tmp1 2>.tmp2
if [ $? -eq 0 ]; then
	echo "Version $PKG_VER exists"
else
	grep -F "Bintray response: 404" .tmp2 >/dev/null
	if [ $? -eq 0 ]; then
		echo "Creating version $PKG_VER"

		TAG_TS=$(GIT_DIR="$JFROG_PKG".git git for-each-ref --format="%(creatordate:iso8601-strict)" refs/tags/"$PKG_VER")
		TAG_DESC=$(GIT_DIR="$JFROG_PKG".git git for-each-ref --format="%(subject)" refs/tags/"$PKG_VER")
		jfrog bt version-create --desc="$TAG_DESC" --vcs-tag="$PKG_VER" --released="$TAG_TS" "$JFROG_VERSION" || exit 1

		jfrog bt version-show "$JFROG_VERSION" 1>.tmp1 2>.tmp2
	else
		echo "Version $PKG_VER unknown error"
		exit 1
	fi
fi

jfrog bt download-file "$JFROG_ORG/$JFROG_REPO/pool/$DEB_RELEASE/main/$JFROG_PKG/${JFROG_PKG}_$PKG_VER.orig.tar.gz" .tmp-null
if [ $? -eq 0 ]; then
	echo "Original source already exists"
else
	echo "Uploading original source"
	jfrog bt upload --publish --deb "$DEB_RELEASE/main/source" "deb/$DEB_DIR/${JFROG_PKG}_$PKG_VER.orig.tar.gz" "$JFROG_VERSION" "pool/$DEB_RELEASE/main/$JFROG_PKG/" || exit 1
fi
rm -rf .tmp-null

jfrog bt download-file "$JFROG_ORG/$JFROG_REPO/pool/$DEB_RELEASE/main/$JFROG_PKG/${JFROG_PKG}_${DEB_VER}.dsc" .tmp-null
if [ $? -eq 0 ]; then
	echo "Files for $TAG already exist"
else
	echo "Uploading debian source"
	jfrog bt upload --publish --deb "$DEB_RELEASE/main/source" "deb/$DEB_DIR/${JFROG_PKG}_$DEB_VER.debian.tar.xz" "$JFROG_VERSION" "pool/$DEB_RELEASE/main/$JFROG_PKG/" || exit 1

	for arch in $ARCHES; do
		echo "Uploading $arch binary"
		jfrog bt upload --publish --deb "$DEB_RELEASE/main/$arch" "deb/$DEB_DIR/${JFROG_PKG}_${DEB_VER}_$arch.deb" "$JFROG_VERSION" "pool/$DEB_RELEASE/main/$JFROG_PKG/" || exit 1

		if [ "$DEB_RELEASE" != "jessie" ] && [ "$DEB_RELEASE" != "xenial" ]; then
			echo "Uploading $arch binary debug symbols"
			jfrog bt upload --publish --deb "$DEB_RELEASE/main/$arch" "deb/$DEB_DIR/${JFROG_PKG}-dbgsym_${DEB_VER}_$arch.$DDEB" "$JFROG_VERSION" "pool/$DEB_RELEASE/main/$JFROG_PKG/" || exit 1
		fi
	done

	echo "Uploading descriptor"
	jfrog bt upload --publish --deb "$DEB_RELEASE/main/source" "deb/$DEB_DIR/${JFROG_PKG}_$DEB_VER.dsc" "$JFROG_VERSION" "pool/$DEB_RELEASE/main/$JFROG_PKG/" || exit 1
fi
rm -rf pool .tmp-null

PUBLISHED=$(python3 -c 'import json, sys; print(json.load(sys.stdin)["published"])' < .tmp1)
if [ "$PUBLISHED" = "True" ]; then
	echo "Version $PKG_VER already published"
elif [ "$PUBLISHED" = "False" ]; then
	echo "Publishing version"
	jfrog bt version-publish "$JFROG_VERSION" || exit 1
else
	echo "Version publish state \"$PUBLISHED\" unknown"
	exit 1
fi

exit 0
