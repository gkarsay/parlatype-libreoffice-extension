#!/bin/bash
# Convenience script to produce an .oxt Extension package.

SOURCE_ROOT=$1
BUILD_ROOT=$2
TEMPDIR=$(mktemp --directory)
OXT="$BUILD_ROOT"/Parlatype.oxt

rm -f "$OXT"

# Add from source root
cd "$SOURCE_ROOT"/extension &&
zip -r "$OXT" \
	images \
	license \
	META-INF \
	options \
	python \
	toolbar \
	--exclude /*meson.build /*.in /*bundled_manifest.xml

# Copy pythonpath from components to macros
mkdir -p "$TEMPDIR"/python/macros
cp -r "$SOURCE_ROOT"/extension/python/components/pythonpath \
      "$TEMPDIR"/python/macros

cd "$TEMPDIR" &&
zip -r "$OXT" python
rm -r "$TEMPDIR"

# Add generated files from build root
cd "$BUILD_ROOT"/extension &&
zip -r "$OXT" \
	description \
	options \
	toolbar \
	description.xml

cd "$BUILD_ROOT"/po &&
zip -r "$OXT" locale