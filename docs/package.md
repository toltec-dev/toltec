## Writing a package recipe

A **package recipe** is a Bash script containing metadata and instructions for building and installing a package.
This recipe is used by the packaging script to generate installable archives for the Opkg package manager.

> **Note:** Recipes should not be marked as executable because they are not meant to be executed directly, but rather to be sourced by the packaging script.

Sourcing a package recipe must have no side-effects, i.e. the metadata section can only execute commands which do not modify the system state, and stateful commands must be confined inside functions.

### Metadata section

At the top of the file is a block of fields which defines metadata about the package.
For consistency, those fields must be declared in the order they are described below.

> **Note:** The field names and semantics is inspired both by the [Debian control file format](https://www.debian.org/doc/debian-policy/ch-controlfields.html) and the [Arch Linux PKGBUILD format](https://wiki.archlinux.org/index.php/PKGBUILD).

#### `pkgname`

<table>
    <tr>
        <th>Required?</th>
        <td>Yes</th>
    </tr>
    <tr>
        <th>Type</th>
        <td>String</td>
    </tr>
</table>

Name of the built package.
Must only contain ASCII lowercase letters, digits and dashes.
Should match the upstream name as closely as possible.

#### `pkgdesc`

<table>
    <tr>
        <th>Required?</th>
        <td>Yes</th>
    </tr>
    <tr>
        <th>Type</th>
        <td>String</td>
    </tr>
</table>

Non-technical description for the package.
This should help a potential user decide if the packaged application will be useful to them.
Must start with a name (e.g. “Scientific calculator” instead of “A scientific calculator”).
Do not explicit the fact that the package is for the reMarkable, because it is redundant (e.g. avoid “Scientific calculator ~~for the reMarkable~~”).

#### `url`

<table>
    <tr>
        <th>Required?</th>
        <td>Yes</th>
    </tr>
    <tr>
        <th>Type</th>
        <td>URL (string)</td>
    </tr>
</table>

Link to the project home page, where sources and documentation may be found.

#### `pkgver`

<table>
    <tr>
        <th>Required?</th>
        <td>Yes</th>
    </tr>
    <tr>
        <th>Type</th>
        <td>Debian-style version number (string)</td>
    </tr>
</table>

Current version of the package.
This is a Debian-style version number, that is equal to the concatenation of Arch-style versioning fields: `$epoch:$pkgver-$pkgrel`.
The [deb-version rules](https://manpages.debian.org/wheezy/dpkg-dev/deb-version.5.en.html) apply:

* Make the newer version number actually greater than all the previous ones, otherwise users will not see it as an available upgrade.
* Always include a package revision number at the end of the version, reseting it to `-1` when bumping the software version, and increasing it when making changes to the recipe itself.
* Match closely the upstream version number.
    - Use the version number `0.0.0` if upstream has no versioning scheme, and then only use the package revision number for increasing the version number.
    - Use the `~beta` suffix for beta versions. `~` has a special meaning in Debian version numbers that makes it sort lower than any other character, even the empty string.

#### `timestamp`

<table>
    <tr>
        <th>Required?</th>
        <td>Yes</th>
    </tr>
    <tr>
        <th>Type</th>
        <td>ISO-8601 timestamp (string)</td>
    </tr>
</table>

ISO-8601-formatted date of publication of the packaged upstream release.
Note that increasing the package version (the part after the final `-`) does not require updating the `timestamp`, as it should only reflect the last modification of the source code.

#### `section`

<table>
    <tr>
        <th>Required?</th>
        <td>Yes</th>
    </tr>
    <tr>
        <th>Type</th>
        <td>String</td>
    </tr>
</table>

Choose one of the following sections:

Section         | Description
----------------|----------------------------------
games           |
launchers       | Automatically started after boot. Presents to the user a list of other apps that can be launched.
math            |
readers         | Document readers (PDF, EPUB, …).
utils           | System tools.

If the package does not fit into one of the existing sections, add a new one to this document. 

#### `maintainer`

<table>
    <tr>
        <th>Required?</th>
        <td>Yes</th>
    </tr>
    <tr>
        <th>Type</th>
        <td>String</td>
    </tr>
</table>

**TODO:** Documentation.

#### `license`

<table>
    <tr>
        <th>Required?</th>
        <td>Yes</th>
    </tr>
    <tr>
        <th>Type</th>
        <td>SPDX identifier (string)</td>
    </tr>
</table>

[SPDX identifier](https://spdx.org/licenses/) of the license under which the upstream allows distribution. Note that this may be different from the license of the recipe file itself.

#### `depends`

<table>
    <tr>
        <th>Required?</th>
        <td>No, defaults to <code>()</code></th>
    </tr>
    <tr>
        <th>Type</th>
        <td>Array of strings</td>
    </tr>
</table>

List of package names that must be installed for this package to work.

See <https://www.debian.org/doc/debian-policy/ch-relationships.html#binary-dependencies-depends-recommends-suggests-enhances-pre-depends>.

#### `conflicts`

<table>
    <tr>
        <th>Required?</th>
        <td>No, defaults to <code>()</code></th>
    </tr>
    <tr>
        <th>Type</th>
        <td>Array of strings</td>
    </tr>
</table>

List of package names that must **NOT** be unpacked for this package to work.

See <https://www.debian.org/doc/debian-policy/ch-relationships.html#conflicting-binary-packages-conflicts>.

#### `image`

<table>
    <tr>
        <th>Required?</th>
        <td>No, defaults to none</th>
    </tr>
    <tr>
        <th>Type</th>
        <td>String</td>
    </tr>
</table>

Docker image used for building this package.
It can be omitted only for packages which do not require a build step (see [below](#build-section-optional)).

#### `source` 

<table>
    <tr>
        <th>Required?</th>
        <td>No, defaults to <code>()</code></th>
    </tr>
    <tr>
        <th>Type</th>
        <td>Array of strings</td>
    </tr>
</table>

**TODO:** Documentation.

#### `sha256sums`

<table>
    <tr>
        <th>Required?</th>
        <td>No, defaults to <code>()</code></th>
    </tr>
    <tr>
        <th>Type</th>
        <td>Array of SHA-256 sums (strings)</td>
    </tr>
</table>

**TODO:** Documentation.

### Build section (optional)

The build section is made up of a function called `build()` which runs in the context of a Docker container with the chosen `image`.
This function has access to all the metadata fields declared above.
The working directory is already populated with all the sources declared in `sources`.
It can be omitted for packages which do not require a build step.

### Package section (required)

The package section is made up of a function called `package()` which runs outside of the Docker container, in an unspecified working directory.
It has access to all the metadata fields, plus the `$srcdir` and `$pkgdir` variables.
The `$pkgdir` directory is initially empty.
The `$srcdir` directory is the working directory of the previous Docker container after running the build section.
The `package()` function populates the `$pkgdir` directory with the files and directories that need to be installed by using files from the `$srcdir` directory.

### Install section (optional)

The install section can contain additional functions to customize the behaviour of the package when it is installed, removed or upgraded on the device.
Those functions are `preinstall()`, `configure()`, `preremove()`, `postremove()`, `preupgrade()` and `postupgrade()`.
Unlike the previous functions, all the install functions **run in the context of the target device.**
They have access to all the metadata fields, but not to other functions.
They can also use functions from the [install library](scripts/install-lib).

When installing a new package, the following happens:

* The package files are unpacked (but not installed)
* `preinstall` is called, if it exists
* The package files are installed into place
* `configure` is called, if it exists

When removing an installed package, the following happens:

* `preremove` is called, if it exists
* The package files are removed (except configuration files)
* `postremove` is called, if it exists

When upgrading a package from version A to B, the following happens:

* `preupgrade B`, if it exists, is called from version A
* Old package files are removed (except configuration files)
* `postupgrade B`, if it exists, is called from version A
* New package files are unpacked and installed
* `configure`, if it exists, is called from version B
