## Toltec

![Status of the stable repository](https://github.com/toltec-dev/toltec/workflows/stable/badge.svg)
![Status of the testing repository](https://github.com/toltec-dev/toltec/workflows/testing/badge.svg)
[![rM1: supported](https://img.shields.io/badge/rM1-supported-green)](https://remarkable.com/store/remarkable)
[![rM2: supported](https://img.shields.io/badge/rM2-supported-green)](https://remarkable.com/store/remarkable-2)
[![Discord](https://img.shields.io/discord/385916768696139794.svg?label=reMarkable&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/ATqQGfu)

Toltec is a community-maintained repository of free software for [the reMarkable tablet](https://remarkable.com/).

### Install it

Toltec works on top of the [Opkg](https://code.google.com/archive/p/opkg/) package manager and the [Entware](https://github.com/Entware/Entware) distribution, which are in widespread use in embedded devices.
To automatically install Opkg, Entware and Toltec, make sure your device is connected to Wi-Fi and run the bootstrap script in an [SSH session](https://remarkablewiki.com/tech/ssh):

```sh
wget http://toltec-dev.org/bootstrap
echo "2d1233271e0cc8232e86827bcb37ab2a44be2c5675cd15f32952614916ae246a  bootstrap" | sha256sum --check && bash bootstrap
```

> **Warning:**
> Do not run `bash bootstrap` without the preceding [SHA-256](https://en.wikipedia.org/wiki/SHA-2) check unless you know what you are doing.
> The check is necessary to prevent [MITM](https://en.wikipedia.org/wiki/Man-in-the-middle_attack) attacks since the built-in `wget` binary does not implement [TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security). The bootstrap script takes care of replacing it with `wget-ssl`.

> **What does this script do?**
> This script will create a `.entware` folder in your home directory, containing a complete Entware distribution (fetched from <https://bin.entware.net/armv7sf-k3.2/>), and permanently mount it to `/opt`.
> It will then configure Opkg for use with Toltec and configure your system to automatically find binaries from `/opt`.
> You are encouraged to [audit the script](scripts/bootstrap/bootstrap).

You now have access to all of the Toltec and Entware packages!
To seamlessly switch between applications, you may want to start by installing a [launcher](https://toltec-dev.org/stable#section-launchers).

[Browse the list of available packages →](https://toltec-dev.org/stable)

### Use it

To install a package:

```sh
opkg install calculator
```

To remove a package:

```sh
opkg remove calculator
```

To update all packages:

```sh
opkg update
opkg upgrade
```

[See information about advanced Opkg commands →](https://openwrt.org/docs/guide-user/additional-software/opkg)

To re-enable Toltec after a system update:

```sh
toltecctl reenable
```

To remove Toltec and all its packages:

```sh
toltecctl uninstall
```

To switch to the testing branch:

```sh
toltecctl switch-branch testing
opkg upgrade
```

[Choose a release branch: _stable_ or _testing_ →](docs/branches.md)

### Build it

This Git repository contains all the tools and recipes required to build the packages published on the package repository.
This repository is automatically built and published every time that a commit is pushed to Git, using [Github Actions](https://docs.github.com/en/actions).
Since all the packaged software in Toltec is free, you can also **build them from source yourself** instead of using the pre-built binaries.
The build process is fully [reproducible](https://reproducible-builds.org/), which means that you can verify that the published packages have not been tampered with during the automated build process.

[Learn how to build the repository from source →](docs/building.md)

### Improve it

Your contribution is welcome for adding new packages, updating existing ones or improving the build tooling.

[Learn how to contribute to Toltec →](docs/contributing.md)
