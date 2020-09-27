# Creating packages


## The goal

The goal is to build and distribute the given program in a `.ipkg` file. The
[toltec](https://github.com/toltec-dev/toltec) git repo's job is to pull in other repositories sourcers, invoke the compilation (if any) and then create a proper `.ipk` file out of it which is then made available [here](https://toltec.delab.re/) to opkg on your reMarkable.


## Creating a package

To create a package please follow this guide.

Clone the [toltec](https://github.com/toltec-dev/toltec) git repo and make sure you're on the `testing` branch which is the default one.


### Creating a directory for your package

Go into the directory `package` and create a directory for your package. This will not determine the final name of that package but should be the same nontheless.

Your package name should be **all lower case** only contain **hyphens** (`-`) at most if really necessary.


### Adding the metadata

Create a file `package`. You can either look at the other examples or create one from this template without the comments (not the vim comment):

#### Your package version (`pkgver`)

The package version should be using [semantic versioning](https://semver.org/). If not possible or used by your software you als may use other formats, but please do not use underscores here. An outlier that doesn't use semantic versioning is [koreader](https://github.com/toltec-dev/toltec/blob/testing/package/koreader/package).  
Please also append `-1` to your version which will indicate different patches to a package without updating the source programs version number. This will be
increased as you make changes to this file or update the used commit to change other files that are not directly tied to your program such as configs or icons for launchers.

`package/your-packagename/package`
```
# vim: set ft=sh:
pkgname=your-package-name
pkgdesc="A short human readable description of what your package is and/or does"
url=https://github.com/username/your-package-repo
pkgver=0.1.0-1
# Time of updating this file in UTC (in 24h format)
timestamp=yyyy-mm-ddThh:mmZ
# A rough section like utils, remarkable-apps (if in launchers), launchers, math, etc.
section=utils
maintainer="Your Name <your_mail@domain.tld>"
# Your license. Examples are MIT, GPL-3.0-or-later, Apache-2.0,  etc.
license=your_license_type
# Optional. Include this to ensure those packages get installed (separated by spaces)
depends=depending-packagename-a depending-packagename-b
# Include this line if your package cant coexist with another one
conflicts=conflicting-packagename

# Which docker image to use. See https://github.com/toltec-dev/toolchain/
# The images are debian based and allow you to install additional packages with apt.
# Examples (version may be out of date): base:v1.1, qt:v1.1, python:v1.1, rust:v1.1
image=base:v1.1
source=(
    https://github.com/username/your-package-repo/archive/FULL_SHA1_OF_COMMIT.zip
)
sha256sums=(
    SHA256_OF_THE_FILE_ABOVE
)

build() {
    # Commands to compile your source
    # You will be in the directory of your specified file in "source="
    # (including that file itself)
    # e.g. make
}

package() {
    # Commands to copy your finished files into the directory
    # that will represent the reMarkable root (/) where those
    # are going to be installed to.
    # You can use simple commands like cp or ln but the
    # command "install" with proper permissions is preferred
    # (`man install` for more or https://linux.die.net/man/1/install)

    # The following environment variables are to be used
    # "$srcdir" - The directory you where in when build() ran
    # "$pkgdir" - The final folder containing the root where your files should go
    # "$recipedir" - `package/your-packagename/`. Contains your package file and others

    # Examples
    # Add a single config file or non-executable resource
    # install -D -m 644 "$srcdir"/default_config "$pkgdir"/opt/etc/your_package.conf
    #
    # Add a empty directory
    # install -d "$pkgdir"/opt/etc/draft/icons
    #
    # Add a executable (binary/script)
    # install -D -m 755 "$srcdir"/build/programname "$pkgdir"/opt/bin/programname
}
```

#### Adding hooks

Should you need to run one or more scripts on certain points you can also add the following scripts (which should be executable and have a [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)))

**NOTE:** This part will probably be changed a bit in the future. See https://github.com/toltec-dev/toltec/issues/60 for more.

The following files are currently available:
- `preinst` - Ran before your package gets installed
- `postinst` - Ran after your package was installed (e.g. to start your systemd service)
- `prerm` - Ran before the package is removed (e.g. to stop systemd service)
- `postrm` - Ran after your package was removed

### Testing your package

Before your create a pull request to [toltec](https://github.com/toltec-dev/toltec), please check that your package build properly to make the review process faster by:
- Installing docker
- Running `make your-package-name`
- Checking and/or manually installing the `.ipk` file found in `build/your-package-name` when creation had no errors


# Bonus


## What is the `.ipk` format?

The package format is pretty similar to debian packages (`.deb`). It is basicially a `.tar.gz` which contains:
- `control.tar.gz`
  - `control` a text file that contains most information of your package like the name, description, dependencies, section, maintainer, etc.
  - `preinst`, `postinst`, `prerm`, `postrm` are simple executable scripts that are run before and after installation/removal respectivly if provided
- `data.tar.gz` contains your binaries, configs, data etc. in a folder structure that mirrors the one when unpacked into the root (`/`) of your device
- `debian-binary` a text file that contains the debian package version number as the structure closly mirrors debians `.deb` packages. In our case it should contain `2.0`.


## Why is it called `.ipk`?

The extension `.ipk` is a shortened version of `ipkg` which is the original name of the software.
> Opkg is a fork of `ipkg`, the package manager used in NSLU2's [Optware](http://www.nslu2-linux.org/wiki/Optware/), which is designed to add software to stock firmware of embedded devices. - [Openwrt's documentation](https://openwrt.org/docs/guide-user/additional-software/opkg)


## What is the difference between entware and opkg?

Entware is a [repository](https://bin.entware.net/) of software that can be used on many embedded devices. It is also present on your opkg installation from [remarkable_entware](https://github.com/Evidlo/remarkable_entware) in `/opt/conf/opkg.conf`.

The term *entware* may be used with opkg interchangably but often means having ipkg/opkg together with the entware repo.

> Opkg is sometimes called Entware, as it is used also in the [Entware repository](http://entware.wl500g.info/) for embedded devices (a fork of OpenWrt community packages repository). - [Openwrt's documentation](https://openwrt.org/docs/guide-user/additional-software/opkg)
