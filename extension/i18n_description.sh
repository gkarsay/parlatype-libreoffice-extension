#!/bin/bash
# Ridiculous hack to automatically translate OpenOffice's <extension-description>


MESON_SOURCE_ROOT="$1"
MESON_BUILD_ROOT="$2"

SOURCE_DIR="$MESON_SOURCE_ROOT"/extension
BUILD_DIR="$MESON_BUILD_ROOT"/extension

cp "$BUILD_DIR"/description.xml.in "$BUILD_DIR"/description.xml

# First get the english text

mkdir -p "$BUILD_DIR"/description
string=$(sed -n 's/<name>\(.*\)<\/name>/\1/p' \
	"$SOURCE_DIR"/description_translation.xml)
echo "$string" > "$BUILD_DIR"/description/desc_en.txt

# Iterate over .po files for all languages
while read -r lang
do
	# Strip comments
	if [[ ${lang:0:1} != "#" && ${lang:0:1} != " " ]]
	then
		# .po files have exactly one translation for source file "translation_source.xml"
		# Get that translation and check if not empty.
		string=$(grep -A 2 'extension/description_translation.xml' "$MESON_SOURCE_ROOT"/po/"$lang".po | sed -n 's/msgstr "\(.*\)"/\1/p')
		if [ "$string" != "" ]
		then
			echo "$string" > "$BUILD_DIR"/description/desc_"$lang".txt
			sed -i "/.*\/extension-description/ i\    <src xlink:href=\"description/desc_$lang.txt\" lang=\"$lang\" />" \
				"$BUILD_DIR"/description.xml
		fi
	fi
done < "$MESON_SOURCE_ROOT"/po/LINGUAS

# LibreOffice description.xml doesn't understand xml:lang attribute
sed -i'' 's/xml:lang/lang/' "$BUILD_DIR"/description.xml