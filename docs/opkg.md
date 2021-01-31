## Opkg and `.ipk` Files

Toltec packages are meant to be used with [Opkg](https://git.yoctoproject.org/cgit/cgit.cgi/opkg), a lightweight package manager targeting embedded devices like the reMarkable.
Opkg is developed both by [OpenWrt](https://git.openwrt.org/project/opkg-lede.git) and by the [Yocto Project](https://git.yoctoproject.org/cgit/cgit.cgi/opkg/).
The Toltec distribution is built on top of [Entware](https://github.com/Entware/Entware) which provides device-agnostic Opkg-compatible packages.

> Opkg is a fork of [ipkg](https://en.wikipedia.org/wiki/Ipkg), the package manager used in NSLU2's [Optware](http://www.nslu2-linux.org/wiki/Optware/), which is designed to add software to stock firmware of embedded devices.
> — [OpenWrt's documentation](https://openwrt.org/docs/guide-user/additional-software/opkg)

### What is the `.ipk` Format?

The package format is similar to Debian packages (`.deb`).
It’s a `.tar.gz` archive with three files:

- `control.tar.gz`: Sub-archive with metadata about the package itself.
    - `control`: Text file containing information about the package.
    See [the Debian documentation](https://www.debian.org/doc/debian-policy/ch-controlfields.html) for details about the value and expected format for each field.
    - `preinst`, `postinst`, `prerm`, `postrm`: Optional shell scripts that are run before and after installation or removal of the package, if provided.
    See [the Debian documentation](https://www.debian.org/doc/debian-policy/ap-flowcharts.html) for more information about when and how those scripts are invoked.
    - `conffiles`: List of files to keep upon upgrading the package (optional).
- `data.tar.gz`: Sub-archive with the actual contents of the package (binaries, configuration files, data) arranged in a folder structure that mirrors the one of your device’s root folder.
- `debian-binary`: Text file that contains the value `2.0`.
Used for telling apart normal `.tar.gz` archives from actual packages.

To see an example of a `.ipk` package, you can download one from Toltec’s [package listing](https://toltec-dev.org/stable) and dissect its contents with your archive manager.

### How are Packages Distributed?

Entware and Toltec both publish repository feeds which list the available packages in a machine-readable format.
([Entware’s feed](https://bin.entware.net/armv7sf-k3.2/Packages), [Toltec’s feed](https://toltec-dev.org/stable/Packages).)
The package manager automatically download the feeds listed in `/opt/etc/opkg.conf`, builds an internal index of available packages, and offers the end-user to manage those packages.

### Other Resources

* [Opkg: Debian’s Little Cousin](https://elinux.org/images/2/24/Opkg_debians_little_cousin.pdf) (Alejandro del Castillo, 2020). A presentation about Opkg’s history, differences and similarities to Debian, and dependency resolution challenges.
* [Managing a custom opkg repository](https://jumpnowtek.com/yocto/Managing-a-private-opkg-repository.html) (Jumpnow Technologies, 2019). Information about what is needed to setup an Opkg repository.
* [Building opkg .ipk packages by hand](https://raymii.org/s/tutorials/Building_IPK_packages_by_hand.html) (Remy van Elst, 2019). Information about how to create a functional `.ipk` package.
