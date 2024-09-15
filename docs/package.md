## Structure of a Recipe

A **recipe** is a Bash script containing the metadata and instructions needed to build a set of related packages from source.
These recipes are used by the packaging script to generate [installable package archives for the Opkg package manager](opkg.md).
Sourcing a recipe must have no side effects: all commands that can affect the system’s state must be confined inside functions.

> **Note:** Recipes should not be marked as executable because they are not meant to be executed directly but rather meant to be parsed by the packaging script.

At the top of the file is a block of fields that define metadata about the package.
A block of functions follows that are run at various steps in the process of building the packages.
You can also declare custom variables to reduce repetition but make sure to prefix their name with `_`.

> **Note:** The metadata fields and functions are inspired both by the [Debian control file format](https://www.debian.org/doc/debian-policy/ch-controlfields.html) and the [Arch Linux PKGBUILD format](https://wiki.archlinux.org/index.php/PKGBUILD).

### Contents

1. [Architecture Section](#architecture-section)
2. [Source Section](#source-section)
3. [Build Section](#build-section)
4. [Package Section](#package-section)
5. [Install Section](#install-section)

### Architecture Section

#### `archs` field

<table>
    <tr>
        <th>Required?</th>
        <td>No, defaults to <code>(rmall)</code></th>
    </tr>
    <tr>
        <th>Type</th>
        <td>Array of strings</td>
    </tr>
</table>

The list of devices that are compatible with this package.
The following values are accepted:

Name        | Meaning
------------|-------------------------------------------------------------------------
`rmall`     | Packages which work on all reMarkable devices without modification.
`rm1`       | Packages requiring reMarkable 1-specific resources or compilation flags.
`rm2`       | Packages requiring reMarkable 2-specific resources or compilation flags.
`rmallos2` | Packages which work on all reMarkable devices without modification, but only on the 2.x series of operating system.
`rm1os2`   | Packages requiring reMarkable 1-specific resources or compilation flags, but only on the 2.x series of operating system.
`rm2os2`   | Packages requiring reMarkable 2-specific resources or compilation flags, but only on the 2.x series of operating system.
`rmallos3` | Packages which work on all reMarkable devices without modification, but only on the 3.x series of operating system.
`rm1os3`   | Packages requiring reMarkable 1-specific resources or compilation flags, but only on the 3.x series of operating system.
`rm2os3`   | Packages requiring reMarkable 2-specific resources or compilation flags, but only on the 3.x series of operating system.

For example, use `archs=(rm1)` for a package that only works on reMarkable 1, or `archs=(rm1 rm2)` for a package that works both on reMarkable 1 and reMarkable 2 but needs different dependencies or compilation flags for each of those.

In the following sections, you can add a suffix to any field to specify that its value only applies to a given architecture.
For string fields, the arch-specific value will replace the unsuffixed value; for array fields, it will be appended to the unsuffixed value.
For example, use `installdepends_rm2=(a b c)` to add reMarkable-2-specific install-time dependencies.

### Source Section

This section tells the packaging script where the source files (or pre-compiled binaries) required to build the recipe can be fetched from.

#### `source` field

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

The list of sources files and archives needed to build the recipe.
The [`build()`](#build-function) and [`package()`](#package-function) functions can access the files referenced in this array from the `$srcdir` directory.
Each entry can either be a local path relative to the recipe file or a URL to a file to fetch from the Internet (using protocols like `http://`, `https://`, or `ftp://`).
Archive files whose names end in `.zip`, `.tar`, `.tar.gz`, `.tar.bz2`, or `.tar.xz` will be automatically extracted in place, with all container directories stripped.
You can disable this behavior by adding the archive name to the `noextract` array.

#### `noextract` field

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
You can provide custom extraction logic in the [`prepare()` function](#prepare-function).
Note that this list should only contain file names, not full paths, in contrast to the `source` array.

#### `sha256sums` field

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

#### `timestamp` field

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

The ISO-8601-formatted date of publication of the upstream release.
Note that increasing the package revision number does not require updating the `timestamp`, as it should only reflect the last modification of the source code.

#### `prepare()` function

The `prepare()` function is run after all the source files have been fetched an extracted, but before any build command is issued.
It has access to all the metadata fields declared above.
Common tasks include patching sources, extracting archives, and moving downloaded sources to the right location.

### Build Section

This section specifies how the source files need to be built and metadata that applies to the whole recipe (instead of specific packages produced by the recipe).

#### `maintainer` field

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
The maintainer is the person in charge of reviewing any pull request regarding the recipe.
This field may be equal to `None <none@example.org>` if a package is orphaned or when proposing a new recipe.

#### `image` field

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

The Docker image and version to use for building the package.
See [the toolchain repo](https://github.com/toltec-dev/toolchain) for a list of available images.
It must be specified if and only if you declare a [`build()` function](#build-function).

#### `flags` field

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

A set of flags that guard special behaviors of the build system.
The following flags are available:

* `nostrip`: Disables the automatic removal of unneeded symbols from binaries and shared libraries.
* `patch_rm2fb`: Patches all the generated binaries to add a dynamic dependency on the [remarkable2-framebuffer](https://github.com/ddvk/remarkable2-framebuffer) client shim.
  Adds an [install-time dependency](#installdepends-field) to all the produced packages on the `rm2fb-shim` package.
  This is an easy way to make apps designed for the reMarkable 1 work on the reMarkable 2 with minimal changes.
  Note: Only binaries that contain the `/dev/fb0` string in their read-only data segment will be patched.

#### `makedepends`

<table>
    <tr>
        <th>Required?</th>
        <td>No, defaults to <code>()</code></th>
    </tr>
    <tr>
        <th>Type</th>
        <td>Array of dependency specifications (strings)</td>
    </tr>
</table>

The list of Debian, Toltec or Entware packages that are needed to build this package.
Dependency specifications have the following format: `[host:|build:]package-name`.
For example, `build:autotools` and `libvncserver>=0.9.13` are valid dependency specifications.

*Build-type dependencies* (prefixed with `build:`) are packages from Debian to install in the container’s root system before the recipe’s build script is executed.

*Host-type dependencies* (prefixed with `host:`) are packages from Toltec or Entware to install in the container’s `$SYSROOT` before the recipe’s build script is executed. The packages are offline-installed (i.e., none of their [install scripts](#install-section) are executed).

**Dependencies declared in the `makedepends` field are only satisfied during the build process, not at install time** — see the [`installdepends`](#installdepends-field) below for declaring install-time dependencies.

#### `pkgnames` field

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

The names of the packages that will be generated from this recipe’s build artifacts.
Unless you’re creating a split package, this array should only contain one entry.
Must only contain ASCII lowercase letters, digits, and dashes.
Should match the upstream name as closely as possible.

#### `build()` function

The `build()` function runs in the context of a Docker container with the chosen `image`.
This function has access to all the metadata variables declared above, plus the `$arch` variable which contains the name of the architecture the recipe is currently being built for.
The working directory is `$srcdir`, which is populated with all the sources declared in `sources`.

### Package Section

This section contains metadata specific to each package generated by the recipe and functions used to generate those packages from the build artifacts created above.
If the `pkgnames` array contains a single value, you can simply declare those fields and functions at the same level as the ones above.
Otherwise, you’re making a so-called _split package_: you’ll need to wrap package-specific fields and metadata into Bash functions named after each package.
The `$pkgname` (singular) variable is available and contains the name of the current package.
Fields defined outside of any function at the top of the recipe will be shared between all generated packages.

#### `pkgdesc` field

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

#### `url` field

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

#### `pkgver` field

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

#### `section` field

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
kernel          | Kernels and modules.
launchers       | Apps that present to the user a list of other apps that they can launch. Usually started automatically after boot.
math            | Apps to assist the user in performing mathematical tasks.
readers         | Apps for reading and annotating documents (PDF, EPUB, …).
screensharing   | Apps for streaming the display between the PC and tablet.
templates       | Templates for xochitl notebooks.
splashscreens   | Splashscreens for device startup, poweroff, suspend, etc.
utils           | System tools and various apps.
writing         | Apps for writing text.

If the package does not fit into one of the existing sections, you are free to create a new one and document it here.

#### `license` field

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

#### `installdepends` field

<table>
    <tr>
        <th>Required?</th>
        <td>No, defaults to <code>()</code></th>
    </tr>
    <tr>
        <th>Type</th>
        <td>Array of dependency specifications (strings)</td>
    </tr>
</table>

The list of Toltec or Entware packages that are needed to install and use this package.
Dependency specifications have the following format: `package-name[(<<|<=|=|=>|>>)version]`.
For example, `xochitl`, `oxide=1.2`, and `draft<<2.0` are valid dependency specifications.

It is guaranteed that all packages declared in this list will be unpacked and configured before this package is configured (i.e., before its `configure()` script is run).
A version constraint can be added after each dependency declaration.
Repeat the dependency twice to specify a version range.

**Dependencies declared in the `installdepends` field are only satisfied at install time, not during the build process** — see the [`makedepends`](#makedepends-field) above for declaring build-time dependencies.

#### `conflicts` field

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

A list of packages that cannot be installed at the same time as this package.
Note that providing the same functionality as another package is not a sufficient reason for declaring a conflict, unless that package cannot be used in the presence of the other package.

#### `replaces` field

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

A list of packages that the current package replaces.
Setting this field allows the current package to overwrite and take ownership of files from other packages.
Note that the replaced packages will not be automatically uninstalled unless you also declare a conflict with them using the [`conflicts` field](#conflicts-field).

#### `provides` field

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

A list of virtual packages that the current package provides.

#### `package()` function

The `package()` function populates the `$pkgdir` directory with the files and directories that need to be installed using artifacts from the `$srcdir` directory.
It runs outside of the Docker container in an unspecified working directory.
It has access to all the metadata fields, the `$arch` and `$pkgname` variables, plus the `$srcdir` and `$pkgdir` paths.
The `$pkgdir` directory is initially empty.

### Install Section

The install section can contain additional functions to customize the behavior of the package when it is installed, removed, or upgraded on the device.
Those functions are `preinstall()`, `configure()`, `preremove()`, `postremove()`, `preupgrade()` and `postupgrade()`.
Unlike the previous functions, all the install functions **run in the context of the target device.**
They have access to all the metadata fields, to custom functions whose name starts with `_`, and to the `$arch` and `$pkgname` variables.
They can also use functions from the [install library](../scripts/install-lib).

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


### reload-oxide-apps hook

If a package contains one or more files in `/opt/etc/draft` or `/opt/usr/share/applications` the `reload-oxide-apps` method in `install-lib` will be appended to the following:

* `configure`
* `postupgrade`
* `postremove`
