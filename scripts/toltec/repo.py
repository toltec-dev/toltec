# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""
Build the package repository.
"""

from datetime import datetime
import gzip
import itertools
import logging
import os
from typing import Dict, List, Optional
import requests
from .recipe import Recipe
from .util import file_sha256, HTTP_DATE_FORMAT
from . import paths, templating

logger = logging.getLogger(__name__)


class Repo:
    """Repository of Toltec packages."""

    def __init__(self) -> None:
        """Initialize the package repository."""
        self.recipes = {}

        for name in os.listdir(paths.RECIPE_DIR):
            if name[0] != ".":
                self.recipes[name] = Recipe.from_file(
                    os.path.join(paths.RECIPE_DIR, name)
                )

    def fetch_packages(
        self, remote: Optional[str], fetch_missing: bool
    ) -> Dict[str, List[str]]:
        """
        Fetch missing packages.

        :param remote: remote server from which to check for existing packages
        :param fetch_missing: pass true to fetch missing packages from remote
        :returns: missing packages grouped by parent recipe
        """
        logger.info("Scanning for missing packages")
        missing: Dict[str, List[str]] = {}

        for recipe in self.recipes.values():
            missing[recipe.name] = []

            for package in recipe.packages.values():
                filename = package.filename()
                local_path = os.path.join(paths.REPO_DIR, filename)

                if os.path.isfile(local_path):
                    continue

                if remote is not None:
                    remote_path = os.path.join(remote, filename)

                    if fetch_missing:
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
                            continue
                    else:
                        req = requests.head(remote_path)
                        if req.status_code == 200:
                            continue

                logger.info(
                    "Package %s (%s) is missing", package.pkgid(), recipe.name
                )
                missing[recipe.name].append(package.name)

        return missing

    def make_index(self) -> None:
        """Generate index files for all the packages in the repo."""
        logger.info("Generating package index")
        index_path = os.path.join(paths.REPO_DIR, "Packages")
        index_gzip_path = os.path.join(paths.REPO_DIR, "Packages.gz")

        with open(index_path, "w") as index_file:
            with gzip.open(index_gzip_path, "wt") as index_gzip_file:
                for recipe in self.recipes.values():
                    for package in recipe.packages.values():
                        filename = package.filename()
                        local_path = os.path.join(paths.REPO_DIR, filename)

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

        listing_path = os.path.join(paths.REPO_DIR, "index.html")
        template = templating.env.get_template("listing.html")

        with open(listing_path, "w") as listing_file:
            listing_file.write(template.render(sections=sections))
