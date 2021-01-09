# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Make ipk packages."""

from gzip import GzipFile
from typing import Dict, IO, Optional
from io import BytesIO
import tarfile
import os


def _targz_open(fileobj: IO[bytes], epoch: int) -> tarfile.TarFile:
    """
    Open a gzip compressed tar archive for writing.

    Modified from :func:`tarfile.TarFile.gzopen` to support
    setting the `mtime` attribute on `GzipFile`.
    """
    gzipobj = GzipFile(
        filename="", mode="wb", compresslevel=9, fileobj=fileobj, mtime=epoch
    )

    try:
        archive = tarfile.TarFile(
            mode="w",
            fileobj=gzipobj,  # type:ignore
            format=tarfile.GNU_FORMAT,
        )
    except:
        gzipobj.close()
        raise

    archive._extfileobj = False  # type:ignore # pylint:disable=protected-access
    return archive


def _clean_info(
    root: Optional[str], epoch: int, info: tarfile.TarInfo
) -> tarfile.TarInfo:
    """
    Remove variable data from an archive entry.

    :param root: absolute path to the root directory from which the
        entry was added, or None to disable turning the name into a
        relative path
    :param epoch: fixed modification time to set
    :param info: tarinfo object to set
    :returns: changed tarinfo
    """
    if root is not None:
        info.name = os.path.relpath("/" + info.name, root)

    if not info.name.startswith("."):
        info.name = "./" + info.name

    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = epoch

    return info


def _add_file(
    archive: tarfile.TarFile, name: str, mode: int, epoch: int, data: bytes
) -> None:
    """
    Add an in-memory file into a tar archive.

    :param archive: archive to append to
    :param name: name of the file to add
    :param mode: permissions of the file
    :param epoch: fixed modification time to set
    :param data: file contents
    """
    info = tarfile.TarInfo("./" + name)
    info.size = len(data)
    info.mode = mode
    archive.addfile(_clean_info(None, epoch, info), BytesIO(data))


def make_control(
    file: IO[bytes], epoch: int, metadata: str, scripts: Dict[str, str]
) -> None:
    """
    Create the control sub-archive.

    See <https://www.debian.org/doc/debian-policy/ch-controlfields.html>
    and <https://www.debian.org/doc/debian-policy/ch-maintainerscripts.html>.

    :param file: file to which the sub-archive will be written
    :param epoch: fixed modification time to set
    :param metadata: package metadata (main control file)
    :param scripts: optional maintainer scripts
    """
    with _targz_open(file, epoch) as archive:
        _add_file(archive, "control", 0o644, epoch, metadata.encode())

        for name, script in scripts.items():
            _add_file(archive, name, 0o755, epoch, script.encode())


def make_data(file: IO[bytes], epoch: int, pkg_dir: str) -> None:
    """
    Create the data sub-archive.

    :param file: file to which the sub-archive will be written
    :param epoch: fixed modification time to set
    :param pkg_dir: directory in which the package tree exists
    """
    with _targz_open(file, epoch) as archive:
        archive.add(
            pkg_dir, filter=lambda info: _clean_info(pkg_dir, epoch, info)
        )


def make_ipk(
    file: IO[bytes],
    epoch: int,
    pkg_dir: str,
    metadata: str,
    scripts: Dict[str, str],
) -> None:
    """
    Create an ipk package.

    :param file: file to which the package will be written
    :param epoch: fixed modification time to set
    :param pkg_dir: directory in which the package tree exists
    :param metadata: package metadata (main control file)
    :param scripts: optional maintainer scripts
    """
    with BytesIO() as control, BytesIO() as data, _targz_open(
        file, epoch
    ) as archive:
        make_control(control, epoch, metadata, scripts)
        _add_file(archive, "control.tar.gz", 0o644, epoch, control.getvalue())

        make_data(data, epoch, pkg_dir)
        _add_file(archive, "data.tar.gz", 0o644, epoch, data.getvalue())

        _add_file(archive, "debian-binary", 0o644, epoch, b"2.0\n")
