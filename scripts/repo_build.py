#!/usr/bin/env python3
# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Build all packages and create a package index."""

import argparse
import logging
import os
from toltec import paths
from toltec.builder import Builder
from toltec.repo import Repo, PackageStatus
from toltec.util import argparse_add_verbose, LOGGING_FORMAT

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument(
    "-d",
    "--diff",
    action="store_true",
    help="only keep new packages that do not exist on the remote repository",
)

argparse_add_verbose(parser)

group = parser.add_mutually_exclusive_group()

group.add_argument(
    "-l",
    "--local",
    action="store_true",
    help="""by default, packages missing from the local repository are not
    rebuilt if they already exist on the remote repository — pass this flag to
    disable this behavior""",
)

group.add_argument(
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
builder = Builder(paths.WORK_DIR, paths.REPO_DIR)
results = repo.fetch_packages(remote)

fetched = results[PackageStatus.Fetched]
missing = results[PackageStatus.Missing]
ordered_missing = repo.order_dependencies(
    [repo.generic_recipes[name] for name in missing]
)

for generic_recipe in ordered_missing:
    if missing[generic_recipe.name]:
        builder.make(generic_recipe, missing[generic_recipe.name])
        repo.make_index()

if args.diff:
    for name in fetched:
        for packages in fetched[name].values():
            for package in packages:
                filename = package.filename()
                local_path = os.path.join(repo.repo_dir, filename)
                os.remove(local_path)

repo.make_index()
repo.make_listing()
