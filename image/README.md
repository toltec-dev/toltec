# toltec Docker image

This Docker image provides a consistent environment for building the packages in the repository.
It is based on Debian Buster and contains:

* [The reMarkable build toolchain](https://remarkable.engineering).
* Additional files for making the toolchain work with CMake.
* [opkg-utils](https://git.yoctoproject.org/cgit/cgit.cgi/opkg-utils/).
* Rust nightly with the armv7-unknown-linux-gnueabihf target
* Git, Python and usual building tools.

Published at <https://hub.docker.com/repository/docker/matteodelabre/toltec>.
