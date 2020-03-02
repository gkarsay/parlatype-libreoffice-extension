# Parlatype LibreOffice Extension

For this LibreOffice extension you need LibreOffice itself and Parlatype <https://www.parlatype.org>.
Parlatype and this extension are released together and should only be used with matching versions.

## Installation methods

LibreOffice extensions can be installed in various ways:
* oxt: A single .oxt file can be installed from within LibreOffice or from commandline. This is the default mode.
* bundled: Extension data is copied to the LibreOffice folder; this is the preferred installation method for distributions.

## Build from source

### Dependencies

To build the extension from source, you need these packages:
* meson >= 0.47.2 (older versions not tested)
* gettext >= 0.19.7
* appstream (only "bundled", main package, not devel version, for metainfo.its rules)
* appstream-utils (optional; if installed, this checks the appstream file)

Runtime dependencies:
* LibreOffice
* Python script support for LibreOffice (e.g on Debian that is libreoffice-script-provider-python, on Fedora libreoffice-pyuno) 
* Parlatype (same version as this extension)


### Configure options

* `bundled`: install as a bundle (default: false)
* `libreoffice-dir`: base folder for LibreOffice, only for "bundled" mode (default: /usr/lib/libreoffice)

### Build as .oxt
First close LibreOffice. If the extension was installed before, remove it with
```
$ unopkg remove parlatype.oxt
```
Continue with
```
$ meson build
$ cd build
$ ninja
$ unopkg add parlatype.oxt
```
This will install the extension for the current user only. You can remove/install it for all users as well with
```
$ sudo unopkg remove --shared parlatype.oxt
[…]
$ sudo unopkg add --shared parlatype.oxt
```
In this mode `ninja install` has no effect.

### Build as a bundle
Prefix decides where AppStream Data is installed, make sure `libreoffice-dir` is set to your LibreOffice base folder (the one containing the folders "presets", "program", "sdk" and "shared").
```
$ meson build --prefix=/usr -Dbundled=true
$ cd build
$ ninja
$ ninja install
```

## Bugs
Please report bugs at https://github.com/gkarsay/parlatype-libreoffice-extension/issues.
