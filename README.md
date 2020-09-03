## about

**Work in progress**

toltec is a community maintained repository of software for the remarkable tablet.

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
* edit package/YOURPACKAGE/package, making sure to bump the version
* build the package (`PACKAGE=YOURPACKAGE scripts/build-package-in-docker`), making sure everything looks ok in artifacts/package/YOURPACKAGE/
* install the package to your tablet, verifying things work as expected
* for new packages, submit a pull request with the title: [$PACKAGE][$VERSION] - New Package
* for updating packages, submit a pull request with the title: [$PACKAGE][$VERSION] - Updated Package
