## Toltec

![Status of the stable repository](https://github.com/matteodelabre/toltec/workflows/stable/badge.svg)
![Status of the testing repository](https://github.com/matteodelabre/toltec/workflows/testing/badge.svg)
[![Discord](https://img.shields.io/discord/463752820026376202.svg?label=reMarkable&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/ATqQGfu)

Toltec is a community-maintained repository of free software for [the reMarkable tablet](https://remarkable.com/).

[Browse the list of available packages →](https://toltec.delab.re/stable)

### Install it

Toltec works with the [Opkg](https://code.google.com/archive/p/opkg/) package manager, which is in widespread use in embedded devices.
Opkg is not available by default on the reMarkable, but you can install it by following the instructions described in [remarkable\_entware](https://github.com/evidlo/remarkable_entware).
After installing Opkg on your device, add the Toltec repository to `/opt/etc/opkg.conf` and download the repository data by running the following commands:

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

[See information about advanced Opkg commands →](https://openwrt.org/docs/guide-user/additional-software/opkg)\
[Choose between the _stable_ and _testing_ channels →](docs/channels.md)

### Build it

This Git repository contains all the tools and recipes required to build the packages published on the package repository.
This repository is automatically built and published every time that a commit is pushed to Git, using [Github Actions](https://docs.github.com/en/actions).
Since all the packaged software in Toltec is free, you can also **build them from source yourself** instead of using the pre-built binaries.
The build process is fully [reproducible](https://reproducible-builds.org/), which means that you can verify that the published packages have not been tampered with during the automated build process.

[Learn how to build the repository from source →](docs/building.md)

### Improve it

Your contribution is welcome for adding new packages, updating existing ones or improving the build tooling.

[Learn how to contribute to Toltec →](docs/contributing.md)
