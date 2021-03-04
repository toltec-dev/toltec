#!/usr/bin/env python3
# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Build packages from a given recipe."""

import argparse
import logging
import sys
from toltec import paths
from toltec.builder import Builder
from toltec.repo import Repo
from toltec.util import argparse_add_verbose, LOGGING_FORMAT

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument(
    "recipe_name",
    metavar="RECIPENAME",
    help="name of the recipe to build",
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

recipe = repo.recipes[args.recipe_name]
packages = (
    [recipe.packages[name] for name in args.packages_names]
    if args.packages_names
    else None
)

if not builder.make(recipe, packages):
    sys.exit(1)

repo.make_index()
