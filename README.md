# Toltec

![Status of the stable repository](https://github.com/matteodelabre/toltec/workflows/stable/badge.svg)
![Status of the testing repository](https://github.com/matteodelabre/toltec/workflows/testing/badge.svg)

Toltec is a community-maintained repository of software for the reMarkable tablet.

## Using

## Building

the core of toltec is this git repository, which contains instructions for
building the packages found in the [toltec.delab.re opkg
repository](https://toltec.delab.re). Whenever a new commit is pushed, the opkg
repository is updated via GitHub Actions.


### building

to build all the packages, run `make` from the base repository. this will
involve downloading a docker image (1GB) and the remarkable toolchain which
will expand to 3GB. the final build artifacts will be found in `artifacts/`.

### adding or updating a package

* clone this repository
* switch to `testing` branch
* edit package/$PACKAGE/package, making sure to bump the version
* build the package (`make $PACKAGE`), making sure everything looks ok in artifacts/package/$PACKAGE/
* install the package to your tablet, verifying things work as expected
* for new packages, submit a pull request with the title: [$PACKAGE][$VERSION] - New Package
* for updating packages, submit a pull request with the title: [$PACKAGE][$VERSION] - Updated Package
