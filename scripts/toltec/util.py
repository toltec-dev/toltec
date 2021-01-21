# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Collection of useful functions."""

import argparse
from collections.abc import Iterable
import hashlib
import logging
import itertools
import os
import shutil
import sys
from typing import Any, Callable, Dict, IO, List, Optional
import zipfile
import tarfile

# Date format used in HTTP headers such as Last-Modified
HTTP_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"

# Logging format for build scripts
LOGGING_FORMAT = "[%(levelname)8s] %(name)s: %(message)s"


def argparse_add_verbose(parser: argparse.ArgumentParser) -> None:
    """Add an option for setting the verbosity level."""
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
        help="show debugging information",
    )


def file_sha256(path: str) -> str:
    """Compute the SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    buffer = bytearray(128 * 1024)
    view = memoryview(buffer)

    with open(path, "rb", buffering=0) as file:
        for length in iter(lambda: file.readinto(view), 0):  # type:ignore
            sha256.update(view[:length])

    return sha256.hexdigest()


def split_all(path: str) -> List[str]:
    """Split a file path into all its directory components."""
    parts = []
    prefix = path

    while prefix not in ("", "/"):
        prefix, base = os.path.split(prefix)
        if base:
            parts.append(base)

    parts.reverse()
    return parts


def all_equal(seq: Iterable) -> bool:
    """Check that all elements of a sequence are equal."""
    grouped = itertools.groupby(seq)
    first = next(grouped, (None, grouped))
    second = next(grouped, None)
    return first and not second


def remove_prefix(filenames: List[str]) -> Dict[str, str]:
    """Find and remove the longest directory prefix shared by all files."""
    split_filenames = [split_all(filename) for filename in filenames]

    # Find the longest directory prefix shared by all files
    min_len = min(len(filename) for filename in split_filenames)
    prefix = 0

    while prefix < min_len and all_equal(
        filename[prefix] for filename in split_filenames
    ):
        prefix += 1

    # If there’s only one file, keep the last component
    if len(filenames) == 1:
        prefix -= 1

    mapping = {}

    for filename, split_filename in zip(filenames, split_filenames):
        if split_filename[prefix:]:
            mapping[filename] = os.path.join(*split_filename[prefix:])

    return mapping


def auto_extract(archive_path: str, dest_path: str) -> bool:
    """
    Automatically extract an archive and strip useless components.

    :param archive_path: path to the archive to extract
    :param dest_path: destination folder for the archive contents
    :returns: true if something was extracted, false if not a supported archive
    """
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path) as zip_archive:
            _auto_extract(
                zip_archive.namelist(),
                zip_archive.getinfo,
                zip_archive.open,
                lambda member: member.is_dir(),
                lambda member: member.external_attr >> 16 & 0x1FF,
                dest_path,
            )
        return True

    if archive_path.endswith(".tar.gz"):
        with tarfile.open(archive_path, mode="r:gz") as tar_archive:
            _auto_extract(
                tar_archive.getnames(),
                tar_archive.getmember,
                tar_archive.extractfile,
                lambda member: member.isdir(),
                lambda member: member.mode,
                dest_path,
            )
        return True

    return False


def _auto_extract(  # pylint:disable=too-many-arguments
    members: List[str],
    getinfo: Callable[[str], Any],
    extract: Callable[[Any], Optional[IO[bytes]]],
    isdir: Callable[[Any], bool],
    getmode: Callable[[Any], int],
    dest_path: str,
) -> None:
    """
    Generic implementation of automatic archive extraction.

    :param members: list of members of the archive
    :param getinfo: get an entry object from an entry name in the archive
    :param extract: get a reading stream corresponding to an archive entry
    :param isdir: get whether an entry is a directory or not
    :param getmode: get the permission bits for an entry
    :param destpath: destinatio folder for the archive contents
    """
    stripped_map = remove_prefix(members)

    for filename, stripped in stripped_map.items():
        member = getinfo(filename)
        file_path = os.path.join(dest_path, stripped)

        if isdir(member):
            os.makedirs(file_path, exist_ok=True)
        else:
            source = extract(member)
            assert source is not None

            with source, open(file_path, "wb") as target:
                shutil.copyfileobj(source, target)

            mode = getmode(member)
            if mode != 0:
                os.chmod(file_path, mode)


def query_user(
    question: str,
    default: str,
    options: Optional[List[str]] = None,
    aliases: Optional[Dict[str, str]] = None,
) -> str:
    """
    Ask the user to make a choice.

    :param question: message to display before the choice
    :param default: default choice if the user inputs an empty string
    :param options: list of valid options (should be lowercase strings)
    :param aliases: accepted aliases for the valid options
    :returns: option chosen by the user
    """
    options = options or ["y", "n"]
    aliases = aliases or {"yes": "y", "no": "n"}

    if default not in options:
        raise ValueError(f"Default value {default} is not a valid option")

    prompt = "/".join(
        option if option != default else option.upper() for option in options
    )

    while True:
        sys.stdout.write(f"{question} [{prompt}] ")
        choice = input().lower()

        if not choice:
            return default

        if choice in options:
            return choice

        if choice in aliases:
            return aliases[choice]

        print("Invalid answer. Please choose among the valid options.")


def list_tree(root: str) -> List[str]:
    """
    Get a sorted list of all files and folders under a given root folder.

    :param root: root folder to start from
    :returns: sorted list of items under the root folder
    """
    result = []

    for directory, _, files in os.walk(root):
        result.append(directory)
        for file in files:
            result.append(os.path.join(directory, file))

    return sorted(result)
