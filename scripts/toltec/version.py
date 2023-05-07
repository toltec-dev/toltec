# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Parse versions and dependency specifications."""

import re
from enum import Enum
from typing import Optional

# Characters permitted in the upstream version part of a version number
_VERSION_CHARS = re.compile("^[A-Za-z0-9.+~-]+$")

# Characters making up a version comparator
_COMPARATOR_CHARS = re.compile("[<>=]")


class VersionComparator(Enum):
    """Operators used to compare two version numbers."""

    # pylint: disable=invalid-name

    LowerThan = "<<"
    LowerThanOrEqual = "<="
    Equal = "="
    GreaterThanOrEqual = ">="
    GreaterThan = ">>"

    # pylint: enable=invalid-name


class InvalidVersionError(Exception):
    """Raised when parsing of an invalid version is attempted."""


class Version:
    """
    Parse package versions.

    See <https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-version>
    for details about the format and the comparison rules.
    """

    def __init__(self, epoch: int, upstream: str, revision: str):
        self.upstream = upstream
        self.revision = revision
        self.epoch = epoch

        if _VERSION_CHARS.fullmatch(upstream) is None:
            raise InvalidVersionError(
                f"Invalid chars in upstream version: '{upstream}'"
            )

        if _VERSION_CHARS.fullmatch(revision) is None:
            raise InvalidVersionError(
                f"Invalid chars in revision: '{revision}'"
            )

        self._original: Optional[str] = None

    @staticmethod
    def parse(version: str) -> "Version":
        """Parse a version number."""
        original = version
        colon = version.find(":")

        if colon == -1:
            epoch = 0
        else:
            epoch = int(version[:colon])
            version = version[colon + 1 :]

        dash = version.find("-")

        if dash == -1:
            revision = "0"
        else:
            revision = version[dash + 1 :]
            version = version[:dash]

        upstream = version

        result = Version(epoch, upstream, revision)
        result._original = original  # pylint:disable=protected-access
        return result

    def __str__(self) -> str:
        if self._original is not None:
            # Use the original parsed version string
            return self._original

        epoch = "" if self.epoch == 0 else f"{self.epoch}:"
        revision = (
            ""
            if self.revision == "0" and "-" not in self.upstream
            else f"-{self.revision}"
        )

        return f"{epoch}{self.upstream}{revision}"

    def __repr__(self) -> str:
        return f"Version(upstream={repr(self.upstream)}, \
revision={repr(self.revision)}, epoch={repr(self.epoch)})"


class DependencyKind(Enum):
    """Kinds of dependencies that may be requested by a package."""

    # pylint: disable=invalid-name

    # Dependency installed in the system used to build a package
    # (e.g., a Debian package)
    Build = "build"
    # Dependency installed alongside a package
    # (e.g., another Entware or Toltec package)
    Host = "host"

    # pylint: enable=invalid-name


class InvalidDependencyError(Exception):
    """Raised when parsing an invalid dependency specification."""


class Dependency:
    """
    Parse version-constrained dependencies.

    Toltec dependencies are declared using the following format:

        [host:|build:]package[(<<|<=|=|=>|>>)version]

    Dependencies of a package that start with `build:` correspond to packages
    that must be installed in the build system. Dependencies that start with
    `host:` or do not have a prefix correspond to packages that must be
    installed alongside the built package, either in the host sysroot when
    building the package, or in the target device when using it.
    """

    def __init__(
        self,
        kind: DependencyKind,
        package: str,
        version_comparator: VersionComparator = VersionComparator.Equal,
        version: Optional[Version] = None,
    ):
        self.kind = kind
        self.package = package
        self.version_comparator = version_comparator
        self.version = version

        self._original: Optional[str] = None

    @staticmethod
    def parse(dependency: str) -> "Dependency":
        """Parse a dependency specification."""
        original = dependency
        kind = DependencyKind.Host

        for enum_kind in DependencyKind:
            if dependency.startswith(enum_kind.value + ":"):
                kind = enum_kind
                dependency = dependency[len(enum_kind.value) + 1 :]
                break

        comp_char_match = _COMPARATOR_CHARS.search(dependency)

        if comp_char_match is None:
            package = dependency
            version_comparator = VersionComparator.Equal
            version = None
        else:
            comp_char = comp_char_match.start()
            for enum_comparator in VersionComparator:
                if dependency[comp_char:].startswith(enum_comparator.value):
                    package = dependency[:comp_char]
                    version_comparator = enum_comparator
                    version = Version.parse(
                        dependency[comp_char + len(enum_comparator.value) :]
                    )
                    break
            else:
                raise InvalidDependencyError(
                    f"Invalid version comparator \
'{dependency[comp_char : comp_char + 2]}'"
                )

        result = Dependency(kind, package, version_comparator, version)
        result._original = original  # pylint:disable=protected-access
        return result

    def to_debian(self) -> str:
        """
        Convert a dependency specification to the Debian format.

        See <https://www.debian.org/doc/debian-policy/ch-relationships.html>
        for the syntax expected by Debian tools.
        """
        if self.version is None:
            return self.package

        return f"{self.package} ({self.version_comparator.value} \
{self.version})"

    def __str__(self) -> str:
        if self._original is not None:
            # Use the original parsed dependency specification
            return self._original

        kind = "build:" if self.kind == DependencyKind.Build else "host:"

        if self.version is None:
            return f"{kind}{self.package}"

        return f"{kind}{self.package}{self.version_comparator.value}\
{self.version}"

    def __repr__(self) -> str:
        return f"Dependency(kind={repr(self.kind)}, \
package={repr(self.package)}, \
version_comparator={repr(self.version_comparator)}, \
version={repr(self.version)})"
