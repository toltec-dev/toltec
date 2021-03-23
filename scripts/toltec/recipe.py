# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""
Parse recipes.

A package is a final user-installable software archive. A recipe is a Bash file
which contains the instructions necessary to build one or more related
packages (in the latter case, it is called a split package).
"""

from dataclasses import dataclass
from itertools import product
from typing import Optional
import os
import textwrap
import dateutil.parser
from .version import Version, Dependency, DependencyKind
from . import bash


class RecipeError(Exception):
    """Raised when a recipe contains an error."""


@dataclass
class Source:
    """Source item needed to build a recipe."""

    url: str
    checksum: str
    noextract: bool


class Recipe:  # pylint:disable=too-many-instance-attributes,disable=too-few-public-methods
    """Load recipes."""

    @staticmethod
    def from_file(path: str) -> "Recipe":
        """
        Load a recipe from its directory.

        :param path: path to the directory containing the recipe definition
        :returns: loaded recipe
        """
        name = os.path.basename(path)
        with open(os.path.join(path, "package"), "r") as recipe:
            return Recipe(name, path, recipe.read())

    def __init__(self, name: str, path: str, definition: str):
        """
        Load a recipe from a Bash source.

        :param name: name of the recipe
        :param path: path to the directory containing the recipe definition
        :param definition: source string of the recipe
        :raises RecipeError: if the recipe contains an error
        """
        self.name = name
        self.path = path
        variables, functions = bash.get_declarations(definition)

        # Original declarations of standard fields and functions
        self.variables: bash.Variables = {}
        self.functions: bash.Functions = {}

        self._load_fields(variables)
        self._load_functions(functions)
        self._load_packages(variables, functions)

        self.custom_variables = variables
        self.custom_functions = functions

    def _load_fields(self, variables: bash.Variables) -> None:
        """Parse and check standard fields."""
        timestamp_str = _pop_field_string(variables, "timestamp")
        self.variables["timestamp"] = timestamp_str

        try:
            self.timestamp = dateutil.parser.isoparse(timestamp_str)
        except ValueError as err:
            raise RecipeError(
                "Field 'timestamp' does not contain a valid ISO-8601 date"
            ) from err

        self.maintainer = _pop_field_string(variables, "maintainer")
        self.variables["maintainer"] = self.maintainer

        self.image = _pop_field_string(variables, "image", "")
        self.variables["image"] = self.image

        self.flags = _pop_field_indexed(variables, "flags", [])
        self.variables["flags"] = self.flags

        sources = _pop_field_indexed(variables, "source", [])
        self.variables["source"] = sources

        sha256sums = _pop_field_indexed(variables, "sha256sums", [])
        self.variables["sha256sums"] = sha256sums

        noextract = _pop_field_indexed(variables, "noextract", [])
        self.variables["noextract"] = noextract

        if len(sources) != len(sha256sums):
            raise RecipeError(
                f"Expected the same number of sources and checksums, got \
{len(sources)} source(s) and {len(sha256sums)} checksum(s)"
            )

        depends_raw = _pop_field_indexed(variables, "depends", [])
        variables["depends"] = depends_raw

        makedepends_raw = _pop_field_indexed(variables, "makedepends", [])
        self.variables["makedepends"] = makedepends_raw

        self.makedepends = [
            Dependency.parse(dep or "") for dep in depends_raw + makedepends_raw
        ]

        self.sources = []

        for source, checksum in zip(sources, sha256sums):
            self.sources.append(
                Source(
                    url=source or "",
                    checksum=checksum or "SKIP",
                    noextract=os.path.basename(source or "") in noextract,
                )
            )

    def _load_functions(self, functions: bash.Functions) -> None:
        """Parse and check standard functions."""
        if self.image and "build" not in functions:
            raise RecipeError(
                "Missing build() function for a recipe which declares a \
build image"
            )

        if not self.image and "build" in functions:
            raise RecipeError(
                "Missing image declaration for a recipe which has a \
build() step"
            )

        self.functions["prepare"] = functions.pop("prepare", "")
        self.functions["build"] = functions.pop("build", "")

    def _load_packages(
        self, variables: bash.Variables, functions: bash.Functions
    ) -> None:
        """Load packages defined by this recipe."""
        self.packages = {}
        pkgnames = _pop_field_indexed(variables, "pkgnames")
        self.variables["pkgnames"] = pkgnames

        if len(pkgnames) == 1:
            # Single-package recipe: use global declarations
            pkg_name = pkgnames[0]
            variables["pkgname"] = pkg_name
            self.packages[pkg_name] = Package(self, variables, functions)
        else:
            # Split-package recipe: load package-local declarations
            pkg_decls = {}

            for pkg_name in pkgnames:
                if pkg_name not in functions:
                    raise RecipeError(
                        "Missing required function {pkg_name}() for \
corresponding package"
                    )

                pkg_def = functions.pop(pkg_name)
                context = bash.put_variables(
                    {
                        **self.variables,
                        **variables,
                        "pkgname": pkg_name,
                    }
                )
                pkg_decls[pkg_name] = bash.get_declarations(context + pkg_def)

                for var_name in self.variables:
                    del pkg_decls[pkg_name][0][var_name]

            for pkg_name, (pkg_vars, pkg_funcs) in pkg_decls.items():
                self.packages[pkg_name] = Package(self, pkg_vars, pkg_funcs)


class Package:  # pylint:disable=too-many-instance-attributes
    """Load packages."""

    def __init__(
        self,
        parent: Recipe,
        variables: bash.Variables,
        functions: bash.Functions,
    ):
        """
        Load a package.

        :param parent: recipe which declares this package
        :param variables: Bash variables declared in the package
        :param functions: Bash functions declared in the package
        :raises RecipeError: if the package contains an error
        """
        self.parent = parent

        # Original declarations of standard fields and functions
        self.variables: bash.Variables = {}
        self.functions: bash.Functions = {}

        self._load_fields(variables)
        self._load_functions(functions)
        self._load_custom(variables, functions)

    def _load_fields(self, variables: bash.Variables) -> None:
        """Parse and check standard fields."""
        self.name = _pop_field_string(variables, "pkgname")
        self.variables["pkgname"] = self.name

        pkgver_str = _pop_field_string(variables, "pkgver")
        self.variables["pkgver"] = pkgver_str
        self.version = Version.parse(pkgver_str)

        self.arch = _pop_field_string(variables, "arch", "armv7-3.2")
        self.variables["arch"] = self.arch

        self.desc = _pop_field_string(variables, "pkgdesc")
        self.variables["pkgdesc"] = self.desc

        self.url = _pop_field_string(variables, "url")
        self.variables["url"] = self.url

        self.section = _pop_field_string(variables, "section")
        self.variables["section"] = self.section

        self.license = _pop_field_string(variables, "license")
        self.variables["license"] = self.license

        depends_raw = _pop_field_indexed(variables, "depends", [])
        self.variables["depends"] = depends_raw
        self.depends = []

        for dep_raw in depends_raw:
            dep = Dependency.parse(dep_raw or "")

            if dep.kind != DependencyKind.Host:
                raise RecipeError(
                    "Only host packages are supported in the 'depends' field"
                )

            self.depends.append(dep)

        conflicts_raw = _pop_field_indexed(variables, "conflicts", [])
        self.variables["conflicts"] = conflicts_raw
        self.conflicts = []

        for conflict_raw in conflicts_raw:
            conflict = Dependency.parse(conflict_raw or "")

            if dep.kind != DependencyKind.Host:
                raise RecipeError(
                    "Only host packages are supported in the 'conflicts' field"
                )

            self.conflicts.append(conflict)

    def _load_functions(self, functions: bash.Functions) -> None:
        """Parse and check standard functions."""
        if "package" not in functions:
            raise RecipeError(
                f"Missing required function package() for package {self.name}"
            )

        self.functions["package"] = functions.pop("package")

        for action in ("preinstall", "configure"):
            self.functions[action] = functions.pop(action, "")

        for rel, step in product(("pre", "post"), ("remove", "upgrade")):
            self.functions[rel + step] = functions.pop(rel + step, "")

    def _load_custom(
        self, variables: bash.Variables, functions: bash.Functions
    ) -> None:
        """Parse and check custom fields and functions."""
        for var_name in variables.keys():
            if not var_name.startswith("_"):
                raise RecipeError(
                    f"Unknown field '{var_name}' in the definition of \
package {self.name} ({self.parent.name}) — make sure to prefix the names of \
custom fields with '_'"
                )

        for func_name in functions.keys():
            if not func_name.startswith("_"):
                raise RecipeError(
                    f"Unknown function '{func_name}' in the definition of \
package {self.name} ({self.parent.name}) — make sure to prefix the names of \
custom functions with '_'"
                )

        self.custom_variables = variables
        self.custom_functions = functions

    def pkgid(self) -> str:
        """Get the unique identifier of this package."""
        return "_".join((self.name, str(self.version), self.arch))

    def filename(self) -> str:
        """Get the name of the archive corresponding to this package."""
        return self.pkgid() + ".ipk"

    def control_fields(self) -> str:
        """Get the control fields for this package."""
        control = textwrap.dedent(
            f"""\
            Package: {self.name}
            Description: {self.desc}
            Homepage: {self.url}
            Version: {self.version}
            Section: {self.section}
            Maintainer: {self.parent.maintainer}
            License: {self.license}
            Architecture: {self.arch}
            """
        )

        if self.depends:
            control += (
                "Depends: "
                + ", ".join(dep.to_debian() for dep in self.depends if dep)
                + "\n"
            )

        if self.conflicts:
            control += (
                "Conflicts: "
                + ", ".join(dep.to_debian() for dep in self.conflicts if dep)
                + "\n"
            )

        return control


# Helpers to check that fields of the right type are defined in a recipe
# and to otherwise return a default value
def _pop_field_string(
    variables: bash.Variables, name: str, default: Optional[str] = None
) -> str:
    if name not in variables:
        if default is None:
            raise RecipeError(f"Missing required field {name}")
        return default

    value = variables.pop(name)

    if not isinstance(value, str):
        raise RecipeError(
            f"Field {name} must be a string, \
got {type(variables[name]).__name__}"
        )

    return value


def _pop_field_indexed(
    variables: bash.Variables,
    name: str,
    default: Optional[bash.IndexedArray] = None,
) -> bash.IndexedArray:
    if name not in variables:
        if default is None:
            raise RecipeError(f"Missing required field '{name}'")
        return default

    value = variables.pop(name)

    if not isinstance(value, list):
        raise RecipeError(
            f"Field '{name}' must be an indexed array, \
got {type(variables[name]).__name__}"
        )

    return value
