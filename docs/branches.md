## Release branches

There are two release branches in Toltec, [stable](https://toltec.delab.re/stable) and [testing](https://toltec.delab.re/testing).
As a user, **you always want to use the stable branch**, which is the default one when following the install instructions.
The testing branch exists solely for the repository maintainers to make sure that packages work correctly before distributing them to users.
It may contain packages that could cause breakage if you install them on your device.

### Adding or updating a package

New packages or package updates are exclusively proposed through pull requests based on the testing branch.
A proposal can be merged into testing after review from a maintainer and if it builds successfully in the CI.
If it is a proposal for a new package, the maintainer who reviews the pull request becomes the maintainer for that package.
If it updates an existing package, the maintainer of that specific package should do the review.

### Moving a package from testing to stable

Each Saturday, a pull request can be opened with selected updates from the testing branch to merge in the stable branch.
This pull request can only be merged from the following Monday.
Each of these package changes must be tested by a maintainer different from the maintainer of the affected package.

Here are important things to check when testing a package:

1. The package should work as intended by upstream.
2. It must not destroy any user data (e.g. from previous versions of the same package, from other packages, from the home directory).
3. It must not break other packages.

### Orphaning a package

The maintainer of a package can, for any reason, choose to orphan a package.
To do so, they need to send a pull request to reset the [`maintainer` metadata field](docs/package.md#maintainer-required) of that package to `None <none@example.org>`.
The next person to review a pull request regarding an orphaned package becomes its new maintainer, and must update the `maintainer` field accordingly.
