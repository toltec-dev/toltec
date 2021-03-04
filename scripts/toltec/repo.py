# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""
Build the package repository.
"""

from collections import namedtuple
from datetime import datetime
import gzip
import itertools
import logging
import os
from typing import Dict, Iterable, List, Optional
import requests
from .graphlib import TopologicalSorter
from .recipe import Package, Recipe
from .util import file_sha256, HTTP_DATE_FORMAT
from .version import DependencyKind
from . import templating

logger = logging.getLogger(__name__)
GroupedPackages = Dict[Recipe, List[Package]]
FetchedMissing = namedtuple("FetchedMissing", ["fetched", "missing"])


class Repo:
    """Repository of Toltec packages."""

    def __init__(self, recipe_dir: str, repo_dir: str) -> None:
        """
        Initialize the package repository.

        :param recipe_dir: directory where recipe definitions are stored
        :param repo_dir: directory where built packages are stored
        """
        self.recipe_dir = recipe_dir
        self.repo_dir = repo_dir
        self.recipes = {}

        for name in os.listdir(self.recipe_dir):
            if name[0] != ".":
                self.recipes[name] = Recipe.from_file(
                    os.path.join(self.recipe_dir, name)
                )

    def fetch_packages(self, remote: Optional[str]) -> FetchedMissing:
        """
        Fetch locally missing packages from a remote server and report which
        packages are missing from the remote and need to be built locally.

        If `remote` is None, no packages are fetched from the network and all
        the packages that are not in the local repo will be considered missing.

        :param remote: remote server from which to check for existing packages
        :returns: tuple containing fetched and missing packages grouped by
            their parent recipe
        """
        logger.info("Scanning for missing packages")
        fetched: GroupedPackages = {}
        missing: GroupedPackages = {}

        for recipe in self.recipes.values():
            fetched[recipe] = []
            missing[recipe] = []

            for package in recipe.packages.values():
                filename = package.filename()
                local_path = os.path.join(self.repo_dir, filename)

                if os.path.isfile(local_path):
                    continue

                if remote is not None:
                    remote_path = os.path.join(remote, filename)
                    req = requests.get(remote_path)

                    if req.status_code == 200:
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
                        fetched[recipe].append(package)
                        continue

                logger.info(
                    "Package %s (%s) is missing", package.pkgid(), recipe.name
                )
                missing[recipe].append(package)

        return FetchedMissing(fetched=fetched, missing=missing)

    @staticmethod
    def order_dependencies(recipes: List[Recipe]) -> Iterable[Recipe]:
        """
        Order a list of recipes so that all recipes that a recipe needs
        come before that recipe in the list.

        :param recipes: list of recipes to order
        :returns: ordered list of recipes
        :raises graphlib.CycleError: if a circular dependency exists
        """
        # See <https://github.com/PyCQA/pylint/issues/2822>
        toposort: TopologicalSorter[  # pylint:disable=unsubscriptable-object
            Recipe
        ] = TopologicalSorter()
        parent_recipes = {}

        for recipe in recipes:
            for package in recipe.packages.values():
                parent_recipes[package.name] = recipe

        for recipe in recipes:
            deps = []

            for dep in recipe.makedepends:
                if (
                    dep.kind == DependencyKind.Host
                    and dep.package in parent_recipes
                ):
                    deps.append(parent_recipes[dep.package])

            toposort.add(recipe, *deps)

        return toposort.static_order()

    def make_index(self) -> None:
        """Generate index files for all the packages in the repo."""
        logger.info("Generating package index")
        index_path = os.path.join(self.repo_dir, "Packages")
        index_gzip_path = os.path.join(self.repo_dir, "Packages.gz")

        with open(index_path, "w") as index_file:
            with gzip.open(index_gzip_path, "wt") as index_gzip_file:
                for recipe in self.recipes.values():
                    for package in recipe.packages.values():
                        filename = package.filename()
                        local_path = os.path.join(self.repo_dir, filename)

                        if not os.path.isfile(local_path):
                            continue

                        control = package.control_fields()
                        control += f"""Filename: {filename}
SHA256sum: {file_sha256(local_path)}
Size: {os.path.getsize(local_path)}

"""

                        index_file.write(control)
                        index_gzip_file.write(control)

    def make_listing(self) -> None:
        """Generate the static web listing for packages in the repo."""
        logger.info("Generating web listing")

        by_section = lambda package: package.section
        packages = [
            package
            for recipe in self.recipes.values()
            for package in recipe.packages.values()
        ]
        sections = dict(
            (section, list(group))
            for section, group in itertools.groupby(
                sorted(packages, key=by_section), key=by_section
            )
        )

        listing_path = os.path.join(self.repo_dir, "index.html")
        template = templating.env.get_template("listing.html")

        with open(listing_path, "w") as listing_file:
            listing_file.write(template.render(sections=sections))
