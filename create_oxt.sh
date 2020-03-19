#!/bin/bash
# Convenience script to produce an .oxt Extension package.

SOURCE_ROOT=$1
BUILD_ROOT=$2

OXT="$BUILD_ROOT"/parlatype.oxt

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

# Add generated files from build root
cd "$BUILD_ROOT"/extension &&
zip -r "$OXT" \
	description \
	options \
	toolbar \
	description.xml

cd "$BUILD_ROOT"/po &&
zip -r "$OXT" locale