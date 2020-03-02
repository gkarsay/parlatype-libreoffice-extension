#!/bin/bash
# Ridiculous hack to automatically translate OpenOffice's <extension-description>
# input:  <sourcedir>/extension/description_translation.xml
#         <sourcedir>/po/<lang>.po
#         <builddir>/extension/description.xml.in.in
# output: <builddir>/extension/description.xml.in
#         <builddir>/extension/description/desc_<lang>.txt

SOURCE_DIR="${MESON_SOURCE_ROOT}"/extension
BUILD_DIR="${MESON_BUILD_ROOT}"/extension

# First get the english text

mkdir -p "$BUILD_DIR"/description
string=`sed -n 's/<name>\(.*\)<\/name>/\1/p' \
	"$SOURCE_DIR"/description_translation.xml`
echo "$string" > "$BUILD_DIR"/description/desc_en.txt

# Iterate over .po files for all languages
while read lang
do
	# Strip comments
	if [[ ${lang:0:1} != "#" && ${lang:0:1} != " " ]]
	then
		# .po files have exactly one translation for source file "translation_source.xml"
		# Get that translation and check if not empty.
		string=`grep -A 2 'extension/description_translation.xml' "${MESON_SOURCE_ROOT}"/po/$lang.po | sed -n 's/msgstr "\(.*\)"/\1/p'`
		if [ "$string" != "" ]
		then
			echo "$string" > "$BUILD_DIR"/description/desc_$lang.txt
			sed "/.*\/extension-description/i <src xlink:href=\"description/desc_$lang.txt\" lang=\"$lang\" />" \
				"$BUILD_DIR"/description.xml.in.in \
				> "$BUILD_DIR"/description.xml.in
		fi
	fi
done < "${MESON_SOURCE_ROOT}"/po/LINGUAS