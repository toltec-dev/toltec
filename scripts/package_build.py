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
from shutil import rmtree
from repo_build import print_disk_usage, cleanup, argparse_add_cleanup
from build import paths
from toltec import parse_recipe  # type: ignore
from toltec.builder import Builder  # type: ignore
from toltec.recipe import Package  # type: ignore
from toltec.repo import make_index  # type: ignore
from toltec.util import argparse_add_verbose, LOGGING_FORMAT  # type: ignore

logger = logging.getLogger(__name__)


def main() -> None:
    """Build a package"""
    parser = argparse.ArgumentParser(description=__doc__)

    _ = parser.add_argument(
        "recipe_name",
        metavar="RECIPENAME",
        help="name of the recipe to build",
    )

    _ = parser.add_argument(
        "-a",
        "--arch-name",
        metavar="ARCHNAME",
        action="append",
        help="""only build for the given architecture (can
        be repeated)""",
    )

    _ = parser.add_argument(
        "packages_names",
        nargs="*",
        metavar="PACKAGENAME",
        help="list of packages to build (default: all packages from the recipe)",
    )

    argparse_add_verbose(parser)
    argparse_add_cleanup(parser)
    args = parser.parse_args()
    logging.basicConfig(format=LOGGING_FORMAT, level=args.verbose)
    builder = Builder(paths.WORK_DIR, paths.REPO_DIR)

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
                        recipes.packages[pkg_name]
                        for pkg_name in args.package_name
                    ]
                else:
                    build_matrix[arch] = None

        rmtree(builder.work_dir, ignore_errors=True)
        try:
            success: bool = builder.make(recipe_bundle, build_matrix, False)

        finally:
            print_disk_usage()

        if args.cleanup:
            cleanup(builder, recipe_bundle)

        if not success:
            sys.exit(1)

        make_index(paths.REPO_DIR)


if __name__ == "__main__":
    main()
