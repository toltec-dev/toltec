## Structure of a package recipe

For consistency, please list the fields in your recipes in the same order as they are described below.

Derived from:

* <https://www.debian.org/doc/debian-policy/ch-controlfields.html>
* <https://wiki.archlinux.org/index.php/PKGBUILD>

### Metadata fields

#### `pkgname` (required)

Name of the built package. Must only contain ASCII lowercase letters, digits and dashes. Should match the name of the upstream as closely as possible.

#### `pkgdesc` (required)

Helpful, non-technical description for the package. This should help a potential user decide if the packaged application will be useful to them. Must start with a name (e.g. “Scientific calculator” instead of “A scientific calculator”). Do not explicit the fact that the package is for the reMarkable, because it is redundant (e.g. avoid “Scientific calculator ~~for the reMarkable~~”).

#### `url` (required)

Link to the project home page.

#### `pkgver` (required)

Current version of the package. This is a Debian-style version number, that is equal to the concatenation of Arch-style versioning fields: `$epoch:$pkgver-$pkgrel`. The [deb-version rules](https://manpages.debian.org/wheezy/dpkg-dev/deb-version.5.en.html) apply, in particular make sure to:

* Make the newer version number actually greater than all the previous ones, otherwise users will not see it as an available upgrade.
* Always include a package revision number at the end of the version, reseting it to `-1` when bumping the software version, and increasing it when making changes to the recipe itself.
* Match closely the upstream version number.
    - Use the version number `0.0.0` if upstream has no versioning scheme, and then only use the package revision number for increasing the version number.
    - Use the `~beta` suffix for beta versions. `~` has a special meaning in Debian version numbers that makes it sort lower than any other character, even the empty string.

#### `timestamp` (required)

ISO-8601-formatted date of publication of the current software version. Note that increasing the package version (the part after the final `-`) does not require updating the `timestamp`, as it should only reflect the last modification of the source code.

#### `section` (required)

Choose one of the following sections:

Section name    | Description
----------------|----------------------------------
games           |
launchers       | Automatically started after boot. Presents to the user a list of other apps that can be launched.
math            |
readers         | Document readers (PDF, EPUB, …).
utils           | System tools.

If the package does not fit into one of the existing sections, add a new one to this document. 

#### `maintainer` (required)

#### `license` (required)

[SPDX identifier](https://spdx.org/licenses/) of the license under which the upstream allows distribution. Note that this may be different from the license of the recipe file itself.

#### `depends` (optional)

Comma-separated list of package names that must be installed for this package to work.

See <https://www.debian.org/doc/debian-policy/ch-relationships.html>.

### Build fields

#### `image` (required)

Docker image used for building this package.

See <../image>.

#### `origin` (required)

URL to the source Git repository used for building this package.

#### `revision` (required)

SHA-1 sum of the commit corresponding to the current package version.

### Functions

#### `build()` (required)

#### `package()` (required)

### Extra files

#### `preinst` (optional)

#### `postinst` (optional)

#### `prerm` (optional)

#### `postrm` (optional)
