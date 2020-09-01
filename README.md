**Work in progress**

opkg: Package manager used by Entware

* https://openwrt.org/docs/guide-user/additional-software/opkg
* https://elinux.org/images/2/24/Opkg_debians_little_cousin.pdf
* https://git.yoctoproject.org/cgit/cgit.cgi/opkg
* https://git.yoctoproject.org/cgit/cgit.cgi/opkg-utils/

## Package format

**ipk**

Inherited from the legacy ipkg tool. Similar to deb.

A tar.gz archive containing two sub-archives:

* data.tar.gz: Files of the package.
    - The structure mirrors that of the root filesystem.
* control.tar.gz: Metadata about the package.
    - Install scripts (optional)
        - preinst: Executed before uncompressing the data.
        - postinst: Executed after the package has been installed.
        - prerm: Executed before uninstalling the package.
        - postrm: Executed after uninstalling the package.
    - Metadata files
        - control: Package description (required).
        - conffiles: Files to keep upon upgrading the package (optional).

### Control file

Fields

* Package: Name of the package (same as in the package archive name).
* Priority: optional.
* Depends: list of space-separated dependencies.
* Section: See <https://packages.debian.org/stable/> for a list of sections in Debian.
* Description: Short description for the package.
* Maintainer: Full Name <email@address.com>
* Source: N/A
* Version: Package version

### See also

* <https://raymii.org/s/tutorials/Building_IPK_packages_by_hand.html>
* <https://bitsum.com/creating_ipk_packages.htm>
* <https://artisan.karma-lab.net/comprendre-paquets-ipk>

## Repository format

Also called a feed.

Directory with list of packages and a `Packages` file

Package naming: `appname_version_arch.ipk`

Config `/opt/etc/opkg.conf`

```
src NAME URL
src/gz NAME URL
```

Where URL is the feed root

### See also

* <https://jumpnowtek.com/yocto/Managing-a-private-opkg-repository.html>
* <https://jumpnowtek.com/yocto/Using-your-build-workstation-as-a-remote-package-repository.html>

## Building

`build-repo`

Date of latest commit

opkg-utils must be in PATH

For reproducibility:

- must be done under the same root path

Automatically updated when commits are pushed to the master branch, via GitHub Actions.
