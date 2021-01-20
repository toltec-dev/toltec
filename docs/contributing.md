## Contributing to Toltec

Thank you for taking the time to contribute to Toltec!
We welcome contributions from anyone, regarding for example [reporting bugs](#reporting-a-bug), [requesting](#requesting-a-package) or [adding new packages](#adding-a-new-package), upgrading existing ones, improving the docs, or other topics.

To make a request or report a bug, you simply need to [open a new issue](../../../issues/new/choose).
To directly propose changes, the basic procedure is:

1. [Fork this repository.](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo)
2. [Create a new branch](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-and-deleting-branches-within-your-repository) off the `testing` branch.\
**This is important! PRs against the default `stable` branch won’t be merged.**
3. Make the desired changes in your newly created local copy.
4. Open a [pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests).

When making your changes, please make sure that you follow the [style guide](#style-guide).
After you submit your pull request, a maintainer will take time to review your changes, request modifications, and then merge your changes into the repository if they fit.

### Common Contributions

#### Requesting a Package

If you would like to see a project packaged in Toltec, you can open an issue to request its addition.
Note that only [free software](https://www.gnu.org/philosophy/free-sw.en.html) can be added to the repository.
Please give at least the following information in your request:

* Where can information about this project be found on the Internet?
* What license is it available under?
* What is it useful for? Describe some use cases.

Your request will be considered by other contributors based on the usefulness of the package and the work required to create and maintain it.
If you’re unsure whether a package is suitable for inclusion in Toltec, you can always drop by the [reMarkable Discord server](https://discord.gg/ATqQGfu) to ask others about it.

#### Reporting a Bug

Found a bug in one of the packages or the install scripts?
To help us fix this, please open an issue and give us as much information as possible:

* What device are you using (reMarkable 1 or reMarkable 2)?
* What mods/hacks/additional software did you install on your device?
* If possible, describe a sequence of steps by which the bug can be reproduced.
* Otherwise, at least describe the context under which the bug occurred.

Please don’t use the issues to ask for help with your device.
Refer to the [reMarkable Discord server](https://discord.gg/ATqQGfu) to ask for assistance instead.
If the bug originates from packaged software itself, it might be more appropriate to report it to the original project.

#### Adding a New Package

The quickest way to add a new package to Toltec is to write the _recipe_ that describes how that package is built then to propose it through a pull request.
See the [guide on how to write a recipe](package-guide.md).
Before proposing your package, make sure that it conforms to the rules on how to [structure a recipe](package.md).

### Style Guide

All contributions must follow the project’s [style guide](../.editorconfig).
Shell scripts must also comply with [Shellcheck](https://github.com/koalaman/shellcheck).
Sticking to a common set of conventions makes it easier for everyone to read the source code and reduces the time spent reviewing little formatting details.

The code style for shell scripts will automatically be checked when you submit your pull request.
You may also check it manually by running `make format` (or `make format-fix` to automatically fix any issues) at the root of the repository (you need to have [shfmt](https://github.com/mvdan/sh) installed on your computer for this to work).

Compliance of shell scripts with Shellcheck will also automatically be checked.
To check it manually, run `make lint` at the root of the repository (you need to have Shellcheck installed on your computer for this to work).

### Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](code_of_conduct.md).
By participating in this project, you agree to abide by its terms.

### License

By contributing to Toltec, you agree to place your contributions under the MIT license.
