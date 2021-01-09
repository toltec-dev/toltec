#!/usr/bin/env python3
# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Build all packages and create a package index."""

import argparse
import logging
from toltec.builder import Builder
from toltec.repo import Repo
from toltec.util import argparse_add_verbose, LOGGING_FORMAT

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument(
    "-n",
    "--no-fetch",
    action="store_true",
    help="do not fetch missing packages from the remote repository",
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

repo = Repo()
builder = Builder()

missing = repo.fetch_packages(remote, fetch_missing=not args.no_fetch)
repo.make_packages(missing)

for recipe_name, packages in missing.items():
    if packages:
        builder.make(recipe_name, packages)

repo.make_index()
