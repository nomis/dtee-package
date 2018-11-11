TAG="$1"
ARCHES="$2"
RPM_DIR="${TAG%%/*}"
RPM_DISTRO="${RPM_DIR%%-*}"
RPM_RELEASE="${RPM_DIR##*-}"
RPM_VER="${TAG##*/}"
PKG_VER="${RPM_VER%%-*}"

case "$RPM_DISTRO" in
	rhel)
		RPM_ID="el$RPM_RELEASE"
		JFROG_REPO=redhat
		;;
	fedora)
		RPM_ID="fc$RPM_RELEASE"
		JFROG_REPO=fedora
		;;
	*)
		echo "Unknown release $RPM_DISTRO"
		exit 1
		;;
esac

JFROG_VERSION="$JFROG_ORG/$JFROG_REPO/$JFROG_PKG/$PKG_VER"

filename="rpm/$RPM_DIR/${JFROG_PKG}-${RPM_VER}.${RPM_ID}.src.rpm"
if [ ! -e "$filename" ]; then
	echo "$filename missing"
	exit 1
fi
chmod a-w "$filename"

if [ "$RPM_DISTRO" = "rhel" ]; then
	VARIANTS=("" "-debuginfo")
else
	VARIANTS=("" "-debuginfo" "-debugsource")
fi

for arch in $ARCHES; do
	for file in "${VARIANTS[@]}"; do
		filename="rpm/$RPM_DIR/${JFROG_PKG}$file-${RPM_VER}.${RPM_ID}.$arch.rpm"
		if [ ! -e "$filename" ]; then
			echo "$filename missing"
			exit 1
		fi
		chmod a-w "$filename"
	done
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

jfrog bt download-file "$JFROG_ORG/$JFROG_REPO/$RPM_RELEASE/source/${JFROG_PKG}-${RPM_VER}.${RPM_ID}.src.rpm" .tmp-null
if [ $? -eq 0 ]; then
	echo "Files for $TAG already exist"
else
	for arch in $ARCHES; do
		for file in "${VARIANTS[@]}"; do
			filename="rpm/$RPM_DIR/${JFROG_PKG}$file-${RPM_VER}.${RPM_ID}.$arch.rpm"
			echo "Uploading $arch binary$file"
			jfrog bt upload --publish "$filename" "$JFROG_VERSION" "$RPM_RELEASE/$arch/" || exit 1
		done
	done

	echo "Uploading source"
	jfrog bt upload --publish "rpm/$RPM_DIR/${JFROG_PKG}-${RPM_VER}.${RPM_ID}.src.rpm" "$JFROG_VERSION" "$RPM_RELEASE/source/" || exit 1
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
