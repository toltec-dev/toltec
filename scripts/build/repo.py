# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""
Build the package repository.
"""
import logging
import os
import pathlib
import shutil

from datetime import datetime
from enum import auto
from enum import Enum
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
)

import requests
from jinja2 import (
    Environment,
    FileSystemLoader,
)
from toltec import parse_recipe  # type: ignore
from toltec.recipe import (
    Package,  # type: ignore
    Recipe,  # type: ignore
)
from toltec.util import HTTP_DATE_FORMAT  # type: ignore
from toltec.version import DependencyKind  # type: ignore

from .graphlib import TopologicalSorter
from .util import group_by

logger = logging.getLogger(__name__)


class PackageStatus(Enum):
    """Possible existence statuses of a built package."""

    # pylint: disable=invalid-name

    # The package already existed in the local filesystem before the build
    AlreadyExists = auto()

    # The package was fetched from a remote repository
    Fetched = auto()

    # The package is missing both from the local filesystem and the remote repo
    Missing = auto()

    # pylint: enable=invalid-name


GroupedPackages = Dict[PackageStatus, Dict[str, Dict[str, List[Package]]]]


class Repo:
    """Repository of Toltec packages."""

    def __init__(self, recipe_dir: str, repo_dir: str) -> None:
        """
        Initialize a package repository.

        :param recipe_dir: directory where recipe definitions are stored
        :param repo_dir: directory where built packages are stored
        """
        self.recipe_dir = recipe_dir
        self.repo_dir = repo_dir
        self.generic_recipes = {}

        for name in os.listdir(self.recipe_dir):
            path = pathlib.Path(self.recipe_dir) / name
            if (
                name[0] != "."
                and os.path.isdir(path)
                and os.path.exists(path / "package")
            ):
                self.generic_recipes[name] = parse_recipe(
                    os.path.join(self.recipe_dir, name)
                )

    def fetch_packages(self, remote: Optional[str]) -> GroupedPackages:
        """
        Fetch locally missing packages from a remote server and report which
        packages are missing from the remote and need to be built locally.

        If `remote` is None, no packages are fetched from the network and all
        the packages that are not in the local repo will be considered missing.

        :param remote: remote server from which to check for existing packages
        :returns: tuple containing fetched and missing packages grouped by
            their parent recipe and architecture
        """
        logger.info("Scanning for missing packages")
        results: GroupedPackages = {
            PackageStatus.Fetched: {},
            PackageStatus.Missing: {},
        }

        for name, generic_recipe in self.generic_recipes.items():
            fetched_generic = {}
            missing_generic = {}

            for arch, recipe in generic_recipe.items():
                fetched_arch = []
                missing_arch = []

                for package in recipe.packages.values():
                    status = self.fetch_package(package, remote)

                    if status == PackageStatus.Fetched:
                        fetched_arch.append(package)
                    elif status == PackageStatus.Missing:
                        logger.info(
                            "Package %s (%s) is missing",
                            package.pkgid(),
                            os.path.basename(recipe.path),
                        )
                        missing_arch.append(package)

                if fetched_arch:
                    fetched_generic[arch] = fetched_arch

                if missing_arch:
                    missing_generic[arch] = missing_arch

            if fetched_generic:
                results[PackageStatus.Fetched][name] = fetched_generic

            if missing_generic:
                results[PackageStatus.Missing][name] = missing_generic

        return results

    def fetch_package(self, package: Package, remote: Optional[str]) -> PackageStatus:
        """
        Check if a package exists locally and fetch it otherwise.

        :param package: package to fetch
        :param remote: remote server from which to check for existing packages
        :param fetch_missing: pass true to fetch missing packages from remote
        :returns: new status of the package
        """
        filename = package.filename()
        local_path = os.path.join(self.repo_dir, filename)

        if os.path.isfile(local_path):
            return PackageStatus.AlreadyExists

        if remote is None:
            return PackageStatus.Missing

        remote_path = os.path.join(remote, filename)

        req = requests.get(remote_path, timeout=5)

        if req.status_code != 200:
            return PackageStatus.Missing

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        with open(local_path, "wb") as local:
            for chunk in req.iter_content(chunk_size=1024):
                local.write(chunk)

        last_modified = int(
            datetime.strptime(
                req.headers["Last-Modified"],
                HTTP_DATE_FORMAT,
            ).timestamp()
        )

        os.utime(local_path, (last_modified, last_modified))
        return PackageStatus.Fetched

    def order_dependencies(
        self,
        generic_recipes: List[Dict[str, Recipe]],
    ) -> Iterable[dict[str, Recipe]]:
        """
        Order a list of recipes so that all recipes that a recipe needs
        come before that recipe in the list.

        :param generic_recipes: list of recipes to order
        :returns: ordered list of recipes
        :raises graphlib.CycleError: if a circular dependency exists
        """
        # See <https://github.com/PyCQA/pylint/issues/2822>
        toposort: TopologicalSorter[  # pylint:disable=unsubscriptable-object
            str
        ] = TopologicalSorter()
        parent_recipes = {}

        for generic_recipe in generic_recipes:
            for recipe in generic_recipe.values():
                for package in recipe.packages.values():  # type: ignore
                    parent_recipes[package.name] = os.path.basename(recipe.path)

        for generic_recipe in generic_recipes:
            for recipe in generic_recipe.values():
                deps = []
                for dep in recipe.makedepends:  # type: ignore
                    if (
                        dep.kind == DependencyKind.HOST
                        and dep.package in parent_recipes
                    ):
                        deps.append(parent_recipes[dep.package])

                toposort.add(os.path.basename(recipe.path), *deps)

        return [self.generic_recipes[name] for name in toposort.static_order()]

    def make_listing(self) -> None:
        """Generate the static web listing for packages in the repo."""
        logger.info("Generating web listing")

        packages = [
            package
            for generic_recipe in self.generic_recipes.values()
            for recipe in generic_recipe.values()
            for package in recipe.packages.values()
        ]

        # Group packages by section and then by shared package name
        sections = {
            section: group_by(section_packages, lambda package: package.name)
            for section, section_packages in group_by(
                packages, lambda package: package.section
            ).items()
        }

        listing_path = os.path.join(self.repo_dir, "index.html")
        template = Environment(
            loader=FileSystemLoader(
                pathlib.Path(__file__).parent.resolve() / ".." / "templates"
            ),
            autoescape=True,
        ).get_template("listing.html")

        # pylint: disable-next=unspecified-encoding
        with open(listing_path, "w") as listing_file:
            listing_file.write(template.render(sections=sections))

    def make_compatibility(self) -> None:
        """Generate the OS compatibility information file."""
        logger.info("Generating compatibility info")
        compat_source = os.path.join(self.recipe_dir, "Compatibility")
        compat_dest = self.repo_dir
        shutil.copy2(compat_source, compat_dest)
