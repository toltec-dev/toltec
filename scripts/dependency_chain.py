#!/usr/bin/env python3
# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Build all packages and create a package index."""

import argparse
import logging
import json
from repo_build import parse_args_and_fetch_packages, argparse_add_cleanup
from build.repo import PackageStatus

logger = logging.getLogger(__name__)


def main() -> None:  # pylint: disable=R0914
    """Build the repo"""

    parser = argparse.ArgumentParser(description=__doc__)

    _ = parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.DEBUG,
        default=logging.ERROR,
        help="show debugging information",
    )
    argparse_add_cleanup(parser)
    _, repo, results = parse_args_and_fetch_packages(parser)
    missing = list(results[PackageStatus.Missing].keys())

    print(
        json.dumps(
            [
                {"recipes": " ".join(names)}
                for names in repo.dependency_chains(missing)
            ],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
