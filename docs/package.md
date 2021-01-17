## Structure of a Recipe

A **recipe** is a Bash script containing the metadata and instructions needed to build a set of related packages from source.
These recipes are used by the packaging script to generate [installable package archives for the Opkg package manager](opkg.md).

> **Note:** Recipes should not be marked as executable because they are not meant to be executed directly but rather meant to be parsed by the packaging script.

Sourcing a recipe must have no side effects: the metadata section can only execute commands that do not modify the system state, and stateful commands must be confined inside functions.

### Contents

1. [Metadata section](#metadata-section)
2. [Prepare section](#prepare-section)
3. [Build section](#build-section)
4. [Package section](#package-section)
5. [Install section](#install-section)
6. [Split packages](#split-packages)

### Metadata Section

At the top of the file is a block of fields that define metadata about the package.
For consistency, declare those fields in the same order they are described below.

> **Note:** The field names and semantics are inspired both by the [Debian control file format](https://www.debian.org/doc/debian-policy/ch-controlfields.html) and the [Arch Linux PKGBUILD format](https://wiki.archlinux.org/index.php/PKGBUILD).

#### `pkgnames`

<table>
    <tr>
        <th>Required?</th>
        <td>Yes</th>
    </tr>
    <tr>
        <th>Type</th>
        <td>Array of strings</td>
    </tr>
</table>

The names of the packages that can be built using this recipe.
Unless you’re creating a [split package](#split-packages), this array should only contain one entry.
Must only contain ASCII lowercase letters, digits, and dashes.
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

A non-technical description for the package.
It should help a potential user decide whether the packaged application can be useful to them.
Must start with a name (e.g., “Scientific calculator” instead of “A scientific calculator”).
Do not explicitly mention that the package is for the reMarkable since it would be redundant (e.g., avoid “Scientific calculator ~~for the reMarkable~~”).

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

A link to the project home page, where users may find sources and documentation.

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

The current version of the package.
A Debian-style version number that is equal to the concatenation of Arch-style versioning fields: `$epoch:$pkgver-$pkgrel`.
The [deb-version rules](https://manpages.debian.org/wheezy/dpkg-dev/deb-version.5.en.html) apply:

* Make newer version numbers greater than all the previous ones, or users will not see them as available upgrades.
* Always include a dash-separated package revision number at the end of the version, resetting it to 1 when bumping the software version, and increasing it when making changes to the recipe itself.
* Match the upstream version number as closely as possible.
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

The ISO-8601-formatted date of publication of the packaged upstream release.
Note that increasing the package revision number does not require updating the `timestamp`, as it should only reflect the last modification of the source code.

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

A single category that best describes the primary purpose of the package. See [the package listing](https://toltec-dev.org/stable) for examples of packages that belong to each section. The following choices currently exist:

Section         | Description
----------------|----------------------------------
admin           | System administration tools.
devel           | Dependencies for other apps, like runtimes or libraries.
drawing         | Apps for drawing and whiteboarding.
games           | Apps for playing games.
launchers       | Apps that present to the user a list of other apps that they can launch. Usually started automatically after boot.
math            | Apps to assist the user in performing mathematical tasks.
readers         | Apps for reading and annotating documents (PDF, EPUB, …).
screensharing   | Apps for streaming the display between the PC and tablet.
templates       | Templates for xochitl notebooks.
utils           | System tools and various apps.

If the package does not fit into one of the existing sections, you are free to create a new one and document it here.

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

The package maintainer’s name and current email address in RFC822 format (e.g., `John Doe <doe@example.org>`).
The maintainer is the person in charge of reviewing any pull request regarding the package.
This field may be equal to `None <none@example.org>` if a package is orphaned or when proposing a new package.

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

[SPDX identifier](https://spdx.org/licenses/) of the license under which the upstream allows distributing the package.
Note that this may be different from the license of the recipe itself, which is always MIT.

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

A list of package names that must be installed on the device before this package can be configured and used.

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

A list of package names that must **NOT** be unpacked at the same time as this package.

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

The Docker image to use for building the package.
It must be omitted for packages that do not require a build step (see [below](#build-section)).
Conversely, you must not define a `build()` function if you omit this field.

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

The list of sources files and archives needed to build the package.
The [`build()`](#build-section) and [`package()`](#package-section) sections can access the files referenced in this array from the `$srcdir` directory.
Each entry can either be a local path relative to the recipe file or a full URL that will be fetched from the Internet (any protocol supported by [curl](https://curl.haxx.se/) can be used here) when building the package.
Archive files whose names end in `.zip`, `.tar.gz`, `.tar.xz`, or `.tar.bz` will be automatically extracted in place, with all container directories stripped.
You can disable this behavior by adding the archive name to the `noextract` array.

#### `noextract`

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

List of archive names which should not be automatically extracted by the build script.
You can provide a custom extraction logic in the [`prepare()` section](#prepare-section).
Note that this list should only contain file names, not full paths, in contrast to the `source` array.

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

List of SHA-256 checksums for the source files.
After copying or downloading a source file to the `$srcdir` directory, the build script will verify its integrity by comparing its checksum with the one registered here.
You can request to skip this verification by entering `SKIP` instead of a valid SHA-256 checksum (discouraged for files fetched from remote computers).
This array must have exactly as many elements as the `source` array.

### Prepare Section

The prepare section contains the `prepare()` function in which the source files may be prepared for the building step that follows.
Common tasks include patching sources, extracting archives, and moving downloaded sources to the right location.

### Build Section

The build section is made up of a function called `build()`, which runs in the context of a Docker container with the chosen `image`.
This function has access to all the metadata fields declared above.
This function will only be run if the `image` field is defined and must be omitted otherwise.
The working directory is already populated with all the sources declared in `sources`.
It can be omitted for packages that do not require a build step.

### Package Section

The package section comprises a function called `package()`, which runs outside of the Docker container in an unspecified working directory.
It has access to all the metadata fields, plus the `$srcdir` and `$pkgdir` variables.
The `$pkgdir` directory is initially empty.
The `$srcdir` directory is the working directory of the previous Docker container after running the build section.
The `package()` function populates the `$pkgdir` directory with the files and directories that need to be installed using files from the `$srcdir` directory.

### Install Section

The install section can contain additional functions to customize the behavior of the package when it is installed, removed, or upgraded on the device.
Those functions are `preinstall()`, `configure()`, `preremove()`, `postremove()`, `preupgrade()` and `postupgrade()`.
Unlike the previous functions, all the install functions **run in the context of the target device.**
They have access to all the metadata fields, but not to other functions.
They can also use functions from the [install library](scripts/install-lib).

When installing a new package, the following happens:

* The package files are unpacked (but not installed)
* `preinstall` is called if it exists
* The package files are installed into place
* `configure` is called if it exists

When removing an installed package, the following happens:

* `preremove` is called if it exists
* The package files are removed (except configuration files)
* `postremove` is called if it exists

When upgrading a package from version A to B, the following happens:

* `preupgrade B`, if it exists, is called from version A
* Old package files are removed (except configuration files)
* `postupgrade B`, if it exists, is called from version A
* New package files are unpacked and installed
* `configure`, if it exists, is called from version B

### Split Packages

Split packages are sets of packages created from the build artifacts of a single recipe.
To create a recipe for split packages, add the names of the additional packages to generate to the [`pkgnames`](#pkgnames) array.
For each package, create a new function bearing the same name as the said package.
Place [metadata fields](#metadata-section), a [package function](#package-section), and optionally [install functions](#install-section) specific to each package inside its associated function.
Fields defined outside of any function at the top of the recipe will be shared with all generated packages.

See [rmkit](../package/rmkit/package) for an example of a split package.
