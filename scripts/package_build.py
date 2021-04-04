#!/usr/bin/env python3
# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Build packages from a given recipe."""

import argparse
import logging
import sys
from typing import Dict, List, Optional
from toltec import paths
from toltec.builder import Builder
from toltec.repo import Repo
from toltec.recipe import Package
from toltec.util import argparse_add_verbose, LOGGING_FORMAT

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

generic_recipe = repo.generic_recipes[args.recipe_name]
arch_packages: Optional[Dict[str, Optional[List[Package]]]] = None

if args.arch_name or args.packages_names:
    arch_packages = {}

    for arch in generic_recipe.recipes.keys():
        if args.packages_names:
            arch_packages[arch] = [
                generic_recipe.recipes[arch].packages[pkg_name]
                for pkg_name in args.packages_names
            ]
        else:
            arch_packages[arch] = None

builder = Builder(paths.WORK_DIR, paths.REPO_DIR)

if not builder.make(generic_recipe, arch_packages):
    sys.exit(1)

repo.make_index()
