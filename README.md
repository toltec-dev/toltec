## Toltec

![Status of the stable repository](https://github.com/toltec-dev/toltec/workflows/stable/badge.svg)
![Status of the testing repository](https://github.com/toltec-dev/toltec/workflows/testing/badge.svg)
[![rM1: supported](https://img.shields.io/badge/rM1-supported-green)](https://remarkable.com/store/remarkable)
[![rM2: supported](https://img.shields.io/badge/rM2-supported-green)](https://remarkable.com/store/remarkable-2)
[![Discord](https://img.shields.io/discord/385916768696139794.svg?label=reMarkable&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/ATqQGfu)

Toltec is a community-maintained repository of free software for the [reMarkable tablet](https://remarkable.com/).

### Installation and Use

Please refer to [the Toltec website](https://toltec-dev.org/) for up-to-date information on how to install and use Toltec.

### Building

This Git repository contains all the tools and recipes required to build the packages published on the package repository.
This repository is automatically built and published every time that a commit is pushed to Git, using [Github Actions](https://docs.github.com/en/actions).
Since all the packaged software in Toltec is free, you can also **build them from source yourself** instead of using the pre-built binaries.
The build process is fully [reproducible](https://reproducible-builds.org/), which means that you can verify that the published packages have not been tampered with during the automated build process.

[Learn how to build the repository from source →](docs/building.md)

### Contributing

Your contribution is welcome for adding new packages, updating existing ones or improving the build tooling.

[Learn how to contribute to Toltec →](docs/contributing.md)
