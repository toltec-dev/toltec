## Toltec

![Status of the stable repository](https://github.com/matteodelabre/toltec/workflows/stable/badge.svg)
![Status of the testing repository](https://github.com/matteodelabre/toltec/workflows/testing/badge.svg)

Toltec is a community-maintained repository of free software for [the reMarkable tablet](https://remarkable.com/).

[Browse the list of available packages →](https://toltec.delab.re/stable)

### Install it

The Toltec repository works with the [Opkg](https://code.google.com/archive/p/opkg/) package manager, which is of widespread use in embedded devices.
Opkg is not available by default on the reMarkable, but you can install it by following the instructions described in [remarkable\_entware](https://github.com/evidlo/remarkable_entware).
After installing Opkg on your device, add the Toltec repository to `/opt/etc/opkg.conf` and update the repository data:

```sh
$ cat "src/gz toltec https://toltec.delab.re/stable" >> /opt/etc/opkg.conf
$ opkg update
```

You now have access to all of the Toltec packages!

### Use it

To install a package:

```sh
$ opkg install calculator
```

To remove a package:

```sh
$ opkg remove calculator
```

To update all packages:

```sh
$ opkg update
$ opkg upgrade
```

### Build it

This Git repository contains all the necessary tools and recipes to build the packages that are published on the package repository.
The package repository is automatically built and published every time that a commit is pushed to the Git repository, through [Github Actions](https://docs.github.com/en/actions).
Since all the packages on Toltec are free software, you can also **build all of the repository’s packages from source yourself** instead of getting them from the package repository.
The build process is fully [reproducible](https://reproducible-builds.org/), which means you can verify that the published packages have not been tampered with during the automated build process.

TODO: Add more information on how to build.

<!-- to build all the packages, run `make` from the base repository. this will
involve downloading a docker image (1GB) and the remarkable toolchain which
will expand to 3GB. the final build artifacts will be found in `artifacts/`. -->

### Improve it

* clone this repository
* switch to `testing` branch
* edit package/$PACKAGE/package, making sure to bump the version
* build the package (`make $PACKAGE`), making sure everything looks ok in artifacts/package/$PACKAGE/
* install the package to your tablet, verifying things work as expected
* for new packages, submit a pull request with the title: [$PACKAGE][$VERSION] - New Package
* for updating packages, submit a pull request with the title: [$PACKAGE][$VERSION] - Updated Package
