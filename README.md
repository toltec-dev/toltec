## Toltec

![Status of the stable repository](https://github.com/toltec-dev/toltec/workflows/stable/badge.svg)
![Status of the testing repository](https://github.com/toltec-dev/toltec/workflows/testing/badge.svg)
[![rm1](https://img.shields.io/badge/rM1-supported-green)](https://remarkable.com/store/remarkable)
[![rm2](https://img.shields.io/badge/rM2-experimental-yellow)](https://remarkable.com/store/remarkable-2)
[![Discord](https://img.shields.io/discord/463752820026376202.svg?label=reMarkable&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/ATqQGfu)

Toltec is a community-maintained repository of free software for [the reMarkable tablet](https://remarkable.com/).

### Install it

Toltec works on top of the [Opkg](https://code.google.com/archive/p/opkg/) package manager and the [Entware](https://github.com/Entware/Entware) distribution, which are in widespread use in embedded devices.
To automatically install Opkg, Entware and Toltec, run the bootstrap script in a [SSH session](https://remarkablewiki.com/tech/ssh) on your reMarkable:

```sh
$ wget http://toltec-dev.org/bootstrap
$ echo "5b494f5b98c4cb5f1d9836f966075026abf48a0cd320a99c026c4b18d76c8a0b  bootstrap" | sha256sum -c
$ bash bootstrap
```

> **Warning:**
> Make sure to run the second line above, which verifies the integrity of the downloaded script before running it.
> Since the built-in wget binary does not implement TLS, _you will expose yourself to MITM attacks if you skip this step!_
> The bootstrap script takes care of replacing the built-in wget with a safer version.

> **What does this script do?**
> This script will create a `.entware` folder in your home directory, containing a complete Entware distribution (fetched from <https://bin.entware.net/armv7sf-k3.2/>), and permanently mount it to `/opt`.
> It will then configure Opkg for use with Toltec and configure your system to automatically find binaries from `/opt`.
> You are encouraged to [audit the script](scripts/bootstrap/bootstrap) yourself if you can.

> **Compatibility with [remarkable_entware](https://github.com/evidlo/remarkable_entware).**
> If you have already installed Entware through Evidlo’s remarkable\_entware, this script will detect the existing install and configure Toltec on top of it.

You now have access to all of the Toltec and Entware packages!

[Browse the list of available packages →](https://toltec-dev.org/stable)

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

[See information about advanced Opkg commands →](https://openwrt.org/docs/guide-user/additional-software/opkg)\
[Choose between _stable_ and _testing_ →](docs/branches.md)

### Build it

This Git repository contains all the tools and recipes required to build the packages published on the package repository.
This repository is automatically built and published every time that a commit is pushed to Git, using [Github Actions](https://docs.github.com/en/actions).
Since all the packaged software in Toltec is free, you can also **build them from source yourself** instead of using the pre-built binaries.
The build process is fully [reproducible](https://reproducible-builds.org/), which means that you can verify that the published packages have not been tampered with during the automated build process.

[Learn how to build the repository from source →](docs/building.md)

### Improve it

Your contribution is welcome for adding new packages, updating existing ones or improving the build tooling.

[Learn how to contribute to Toltec →](docs/contributing.md)
