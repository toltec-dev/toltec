#!/usr/bin/env python3
# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Build packages from a given recipe."""

import argparse
import logging
import os
import sys
from typing import (
    Dict,
    List,
    Optional,
)
from build import paths
from build.repo import Repo
from toltec import parse_recipe  # type: ignore
from toltec.builder import Builder  # type: ignore
from toltec.recipe import Package  # type: ignore
from toltec.repo import make_index  # type: ignore
from toltec.util import argparse_add_verbose, LOGGING_FORMAT  # type: ignore

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument(
    "recipe_name",
    metavar="RECIPENAME",
    help="name of the recipe to build",
)

parser.add_argument(
    "-a",
    "--arch-name",
    metavar="ARCHNAME",
    action="append",
    help="""only build for the given architecture (can
    be repeated)""",
)

parser.add_argument(
    "packages_names",
    nargs="*",
    metavar="PACKAGENAME",
    help="list of packages to build (default: all packages from the recipe)",
)

argparse_add_verbose(parser)

args = parser.parse_args()
logging.basicConfig(format=LOGGING_FORMAT, level=args.verbose)
repo = Repo(paths.RECIPE_DIR, paths.REPO_DIR)
builder = Builder(paths.WORK_DIR, paths.REPO_DIR)
arch_packages: Optional[Dict[str, Optional[List[Package]]]] = None

with Builder(
    os.path.join(paths.WORK_DIR, args.recipe_name), paths.REPO_DIR
) as builder:
    recipe_bundle = parse_recipe(f"package/{args.recipe_name}")
    build_matrix: Optional[Dict[str, Optional[List[Package]]]] = None
    if args.arch_name or args.packages_names:
        build_matrix = {}
        for arch, recipes in recipe_bundle.items():
            if args.package_name:
                build_matrix[arch] = [
                    recipes.packages[pkg_name] for pkg_name in args.package_name
                ]
            else:
                build_matrix[arch] = None

    if not builder.make(recipe_bundle, build_matrix, False):
        sys.exit(1)

    make_index(paths.REPO_DIR)
