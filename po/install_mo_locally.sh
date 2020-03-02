#!/bin/bash
# Install generated translations locally.

SOURCE_DIR="${MESON_SOURCE_ROOT}"/po
BUILD_DIR="${MESON_BUILD_ROOT}"/po/locale


mkdir -p "$BUILD_DIR"

# Iterate over .po files for all languages
while read lang
do
	if [[ ${lang:0:1} != "#" && ${lang:0:1} != " " ]]
	then
		DEST_DIR="$BUILD_DIR"/$lang/LC_MESSAGES
		mkdir -p "$DEST_DIR"
		msgfmt $lang.po -o "$DEST_DIR"/parlatype_lo.mo
	fi
done < "$SOURCE_DIR"/LINGUAS
