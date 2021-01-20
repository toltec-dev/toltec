## Creating Package Recipes

This guide will teach you how to make a recipe for building a Toltec package for the program of your choice.

### Contents

1. [Getting Started](#metadata-section)
2. [Creating a Directory for your Package](#prepare-section)
3. [Writing the Recipe](#writing-the-recipe)
4. [Testing your Package](#testing-your-package)

### Getting Started

First, you need a local copy of the Toltec source code to work on.
Fork and clone the [Toltec](https://github.com/toltec-dev/toltec) Git repository:

```sh
git clone https://github.com/<username>/toltec
```

Create a new branch for your work, based on the `testing` branch.
You need to choose a name for your branch — we suggest using the `package/<name>` format, where `<name>` is the name of the project you’re packaging.

```sh
git switch -c package/<name> origin/testing
```

### Creating a Directory for your Package

All recipes are stored in the `package/` folder.
Change to that directory and create a new subfolder for your package.
The name of this folder must reflect the name of the project you’re packaging.
It should be all lower case and only contain alphabetic characters and hyphens if necessary.

### Writing the Recipe

Create a new file named `package` in the new directory.
Start with the following template (remove helper comments and replace placeholders with correct values).

`package/<name>/package`
```sh
#!/usr/bin/env bash
# Copyright (c) 2020 The Toltec Contributors
# SPDX-License-Identifier: MIT

pkgnames=(<name>)
## This should be a short description targeted at users of your package
# Start directly with a noun or a verb, do not include “for the reMarkable”
pkgdesc="<description>"
## URL to where the project can be found on the Internet
url="<project homepage URL>"
## Version of the package (see below)
pkgver=0.0.0-1
## ISO-8601 timestamp at which the source of this version was released
timestamp=<source release date>
## Section that best matches this package
# See <https://github.com/toltec-dev/toltec/blob/stable/docs/package.md#section>
# for available sections
section=<section>
## This should be your contact information
maintainer="Your Name <your@email.com>"
## A license under which the upstream source is available
# Choose among the list of valid SPDX license identifiers
# <https://spdx.org/licenses/>
license=<project license>

## Which Docker image to use for building the package
# See <https://github.com/toltec-dev/toolchain> for available images
# The images are debian based and allow you to install additional packages with apt.
# Examples (version may be out of date): base:v1.1, qt:v1.1, python:v1.1, rust:v1.1
image=<build image>
## Whitespace-separated list of source archives that are needed to build the package
# Archives will be automatically extracted, stripping any useless containing
# directories, and made available during the build step below
source=(
    https://github.com/<username>/<name>/archive/<commit>.zip
)
## SHA-256 checksums of the source archives above
sha256sums=(
    <SHA-256 checksum>
)

build() {
    ## Commands to compile your source
    # The working directory contains all sources specified in `source=`
    # above, with archives already extracted
}

package() {
    ## Commands to copy the build artifacts into a package structure
    # Use the `install` command when possible
    # (see `man install` or <https://linux.die.net/man/1/install>)

    # The following variables are available:
    # "$srcdir" - The directory where build() was run
    # "$pkgdir" - The final folder containing the root where your files should go

    # Examples:
    # Add a single config file or non-executable resource
    # install -D -m 644 "$srcdir"/default_config "$pkgdir"/opt/etc/your_package.conf
    #
    # Add a empty directory
    # install -d "$pkgdir"/opt/etc/draft/icons
    #
    # Add a executable (binary/script)
    # install -D -m 755 "$srcdir"/build/programname "$pkgdir"/opt/bin/programname
}
```

The package version (in `pkgver`) should reflect the package version of the source project.
You may only use alphanumeric characters, `.`, `+`, `-` and `~`.
The version number must start with a digit.
Append a dash-separated package revision number, starting at `1`, to the upstream version.
This number is increased whenever the recipe is changed but the source stays the same.

This template only presents the basic features of a recipe.
Refer to [the full documentation](package.md) for more features and more details.

### Testing your Package

Once your recipe is ready, change back to the repository root and run `make <name>` to launch the build.
If the build completes without errors, use the following procedure to test out your package:

1. Plug in the tablet via USB.
2. Use `make <name>-push` to copy the resulting package to your device.
3. Start a SSH session and run `opkg install .cache/opkg/<name>.ipk` to install the package.
4. Make sure that everything is working.
5. Use `opkg remove <name>` to uninstall the package.

If everything works, congrats! You’re all set to open a pull request.
