#!/usr/bin/env python3
# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Build all packages and create a package index."""

import argparse
import logging
import os
from typing import (
    Dict,
    List,
    Optional,
)
from shutil import disk_usage, rmtree
from build import paths
from build.repo import Repo, PackageStatus
from toltec.recipe import Package, RecipeBundle  # type: ignore
from toltec import parse_recipe  # type: ignore
from toltec.builder import Builder  # type: ignore
from toltec.repo import make_index  # type: ignore
from toltec.util import argparse_add_verbose, LOGGING_FORMAT  # type: ignore

logger = logging.getLogger(__name__)


def sizeof_fmt(num: float, suffix: str = "B") -> str:
    """Output human readable string for size in bytes"""
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"

        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def cleanup(builder: Builder, recipe_bundle: RecipeBundle) -> None:
    """Perform cleanup to reduce space usage"""
    rmtree(builder.work_dir, ignore_errors=True)
    for image in {x.image for x in recipe_bundle.values() if x.image}:
        builder.docker.images.remove(builder.IMAGE_PREFIX + image)


def print_disk_usage() -> None:
    """Print the current disk usage for important paths"""
    usage = disk_usage(paths.WORK_DIR)
    logger.info(
        "work_dir: %s/%s",
        sizeof_fmt(usage.used),
        sizeof_fmt(usage.total),
    )
    usage = disk_usage(paths.REPO_DIR)
    logger.info(
        "repo_dir: %s/%s",
        sizeof_fmt(usage.used),
        sizeof_fmt(usage.total),
    )


def argparse_add_cleanup(parser: argparse.ArgumentParser) -> None:
    """Add the cleanup argument"""
    _ = parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove the work folder after finishing building the recipe",
    )


def main() -> None:  # pylint: disable=R0914
    """Build the repo"""

    parser = argparse.ArgumentParser(description=__doc__)

    _ = parser.add_argument(
        "-d",
        "--diff",
        action="store_true",
        help="only keep new packages that do not exist on the remote repository",
    )

    argparse_add_verbose(parser)
    argparse_add_cleanup(parser)

    group = parser.add_mutually_exclusive_group()

    _ = group.add_argument(
        "-l",
        "--local",
        action="store_true",
        help="""by default, packages missing from the local repository are not
        rebuilt if they already exist on the remote repository — pass this flag to
        disable this behavior""",
    )

    _ = group.add_argument(
        "-r",
        "--remote-repo",
        default="https://toltec-dev.org/testing",
        metavar="URL",
        help="""root of a remote repository used to know which packages
        are already built (default: %(default)s)""",
    )
    args = parser.parse_args()
    remote = args.remote_repo if not args.local else None
    logging.basicConfig(format=LOGGING_FORMAT, level=args.verbose)

    repo = Repo(paths.RECIPE_DIR, paths.REPO_DIR)
    results = repo.fetch_packages(remote)

    os.makedirs(paths.REPO_DIR, exist_ok=True)
    make_index(paths.REPO_DIR)

    fetched = results[PackageStatus.Fetched]
    missing = results[PackageStatus.Missing]
    ordered_missing = repo.order_dependencies(
        [repo.generic_recipes[name] for name in missing]
    )

    for generic_recipe in ordered_missing:
        # Will need to rework toltec_old.repo into something inline and actually easy to work
        # with Currently generic_recipe is a Dict[str, Recipe] where the index is the arch. Every
        # single entry will have the same path, so we can use that for the name of the generic
        # recipe we are actually building.
        name = os.path.basename(next(iter(generic_recipe.values())).path)
        if missing[name]:
            with Builder(
                os.path.join(paths.WORK_DIR, name), paths.REPO_DIR
            ) as builder:
                rmtree(builder.work_dir, ignore_errors=True)
                recipe_bundle = parse_recipe(
                    os.path.join(paths.RECIPE_DIR, name)
                )
                build_matrix: Optional[Dict[str, Optional[List[Package]]]] = (
                    None
                )
                old_build_matrix = missing[name]
                if old_build_matrix:
                    build_matrix = {}

                    for arch in old_build_matrix.keys():
                        build_matrix[arch] = [
                            recipe_bundle[arch].packages[pkg_name]
                            for pkg_name in recipe_bundle[arch].packages
                        ]
                logger.info("Building %s", name)
                try:
                    builder.make(recipe_bundle, build_matrix, False)

                finally:
                    print_disk_usage()

                if args.cleanup:
                    cleanup(builder, recipe_bundle)

            make_index(paths.REPO_DIR)

    if args.diff:
        for name in fetched:
            for packages in fetched[name].values():
                for package in packages:
                    filename = package.filename()
                    local_path = os.path.join(repo.repo_dir, filename)
                    os.remove(local_path)

    make_index(paths.REPO_DIR)
    repo.make_listing()
    repo.make_compatibility()


if __name__ == "__main__":
    main()
