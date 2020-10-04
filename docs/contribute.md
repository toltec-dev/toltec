## Contributing to Toltec

**TODO**

### Adding a new package

See [instructions for creating a package recipe](package.md).

* clone this repository
* switch to `testing` branch
* edit package/$PACKAGE/package, making sure to bump the version
* build the package (`make $PACKAGE`), making sure everything looks ok in artifacts/package/$PACKAGE/
* install the package to your tablet, verifying things work as expected
* for new packages, submit a pull request with the title: [$PACKAGE][$VERSION] - New Package
* for updating packages, submit a pull request with the title: [$PACKAGE][$VERSION] - Updated Package
