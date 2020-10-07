## Contributing to Toltec

Thank you for taking time to contribute to Toltec!
We welcome contributions from anyone, regarding for example [reporting bugs](#reporting-a-bug), [requesting](#request-a-package) or [adding new packages](#adding-a-new-package), [upgrading existing ones](#upgrading-a-package), [improving the docs](#improving-the-documentation), or other topics.

To make a request or report a bug, you simply need to [open a new issue](../../../issues/new/choose).

To directly propose changes, the basic procedure is to fork this repository, make the desired changes in your newly created local copy, and open a pull request.
When proposing changes, please make sure that you follow the [style guide](#style-guide).
After you submit your pull request, a maintainer will take time to review your changes, request modifications and then merge your changes into the repository if they fit.

### Common contributions

#### Requesting a package

**TODO**

#### Reporting a bug

**TODO**

#### Adding a new package

See [instructions for creating a package recipe](package.md).

* clone this repository
* switch to `testing` branch
* edit package/$PACKAGE/package, making sure to bump the version
* build the package (`make $PACKAGE`), making sure everything looks ok in artifacts/package/$PACKAGE/
* install the package to your tablet, verifying things work as expected
* for new packages, submit a pull request with the title: [$PACKAGE][$VERSION] - New Package
* for updating packages, submit a pull request with the title: [$PACKAGE][$VERSION] - Updated Package

#### Upgrading a package

**TODO**

#### Improving the documentation

**TODO**

### Style guide

All contributions must follow the project’s [style guide](../.editorconfig).
Shell scripts must also comply to [Shellcheck](https://github.com/koalaman/shellcheck).
Sticking to a common set of conventions makes it easier for everyone to read the source code and reduces the time spent reviewing little formatting details.

The code style for shell scripts will automatically be checked when you submit your pull request.
You may also check it manually by running `make format` (or `make format-fix` to automatically fix any issues) at the root of the repository (you need to have [shfmt](https://github.com/mvdan/sh) installed on your computer for this to work).

Compliance of shell scripts to Shellcheck will also automatically be checked.
To check it manually, run `make lint` at the root of the repository (you need to have Shellcheck installed on your computer for this to work).

### License

By contributing to Toltec, you agree to place your contributions under the MIT license.
