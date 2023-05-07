# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Build recipes and create packages."""

import shutil
from typing import (
    Any,
    Dict,
    Deque,
    List,
    Mapping,
    MutableMapping,
    NamedTuple,
    Optional,
    Tuple,
)
from collections import deque
import re
import os
import shlex
import logging
import textwrap
import docker
from elftools.elf.elffile import ELFFile, ELFError
import requests
from . import bash, util, ipk, paths
from .recipe import GenericRecipe, Recipe, Package, BuildFlags
from .version import DependencyKind

logger = logging.getLogger(__name__)


class BuildError(Exception):
    """Raised when a build step fails."""


class PostprocessingCandidates(NamedTuple):
    """List of binaries on which post-processing needs to be done."""

    strip_arm: List[str]
    strip_x86: List[str]
    patch_rm2fb: List[str]


class BuildContextAdapter(logging.LoggerAdapter):
    """Prefix log entries with information about the current build target."""

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> Tuple[str, MutableMapping[str, Any]]:
        prefix = ""

        if "recipe" in self.extra:
            prefix += self.extra["recipe"]

        if "arch" in self.extra:
            prefix += f" [{self.extra['arch']}]"

        if "package" in self.extra:
            prefix += f" ({self.extra['package']})"

        if prefix:
            return f"{prefix}: {msg}", kwargs

        return msg, kwargs


class Builder:  # pylint: disable=too-few-public-methods
    """Helper class for building recipes."""

    # Detect non-local paths
    URL_REGEX = re.compile(r"[a-z]+://")

    # Prefix for all Toltec Docker images
    IMAGE_PREFIX = "ghcr.io/toltec-dev/"

    # Toltec Docker image used for generic tasks
    DEFAULT_IMAGE = "toolchain:v1.3.1"

    def __init__(self, work_dir: str, repo_dir: str) -> None:
        """
        Create a builder helper.

        :param work_dir: directory where packages are built
        :param repo_dir: directory where built packages are stored
        """
        self.work_dir = work_dir
        os.makedirs(work_dir, exist_ok=True)

        self.repo_dir = repo_dir
        os.makedirs(repo_dir, exist_ok=True)

        self.install_lib = ""
        install_lib_path = os.path.join(paths.SCRIPTS_DIR, "install-lib")

        self.context: Dict[str, str] = {}
        self.adapter = BuildContextAdapter(logger, self.context)

        # pylint: disable-next=unspecified-encoding
        with open(install_lib_path, "r") as file:
            for line in file:
                if not line.strip().startswith("#"):
                    self.install_lib += line

        try:
            self.docker = docker.from_env()
        except docker.errors.DockerException as err:
            raise BuildError(
                "Unable to connect to the Docker daemon. \
Please check that the service is running and that you have the necessary \
permissions."
            ) from err

    def make(
        self,
        generic_recipe: GenericRecipe,
        arch_packages: Optional[Mapping[str, Optional[List[Package]]]] = None,
    ) -> bool:
        """
        Build packages defined by a recipe.

        :param generic_recipe: recipe to make
        :param arch_packages: set of packages to build for each
            architecture (default: all supported architectures
            and all declared packages)
        :returns: true if all the requested packages were built correctly
        """
        self.context["recipe"] = generic_recipe.name
        build_dir = os.path.join(self.work_dir, generic_recipe.name)

        if not util.check_directory(
            build_dir,
            f"The build directory '{os.path.relpath(build_dir)}' for recipe \
'{generic_recipe.name}' already exists.\nWould you like to [c]ancel, [r]emove \
that directory, or [k]eep it (not recommended)?",
        ):
            return False

        for name in (
            list(arch_packages.keys())
            if arch_packages is not None
            else list(generic_recipe.recipes.keys())
        ):
            if not self._make_arch(
                generic_recipe.recipes[name],
                os.path.join(build_dir, name),
                arch_packages[name] if arch_packages is not None else None,
            ):
                return False

        return True

    def _make_arch(
        self,
        recipe: Recipe,
        build_dir: str,
        packages: Optional[List[Package]] = None,
    ) -> bool:
        self.context["arch"] = recipe.arch

        src_dir = os.path.join(build_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        self._fetch_sources(recipe, src_dir)
        self._prepare(recipe, src_dir)

        base_pkg_dir = os.path.join(build_dir, "pkg")
        os.makedirs(base_pkg_dir, exist_ok=True)

        self._build(recipe, src_dir)
        self._postprocessing(recipe, src_dir)

        for package in packages if packages is not None else recipe.packages.values():
            self.context["package"] = package.name
            pkg_dir = os.path.join(base_pkg_dir, package.name)
            os.makedirs(pkg_dir, exist_ok=True)

            self._package(package, src_dir, pkg_dir)
            self._archive(package, pkg_dir)
            del self.context["package"]

        del self.context["arch"]
        return True

    def _fetch_sources(
        self,
        recipe: Recipe,
        src_dir: str,
    ) -> None:
        """Fetch and extract all source files required to build a recipe."""
        self.adapter.info("Fetching source files")

        for source in recipe.sources:
            filename = os.path.basename(source.url)
            local_path = os.path.join(src_dir, filename)

            if self.URL_REGEX.match(source.url) is None:
                # Get source file from the recipe’s directory
                shutil.copy2(os.path.join(recipe.parent.path, source.url), local_path)
            else:
                # Fetch source file from the network
                req = requests.get(source.url, timeout=5)

                if req.status_code != 200:
                    raise BuildError(
                        f"Unexpected status code while fetching \
source file '{source.url}', got {req.status_code}"
                    )

                with open(local_path, "wb") as local:
                    for chunk in req.iter_content(chunk_size=1024):
                        local.write(chunk)

            # Verify checksum
            file_sha = util.file_sha256(local_path)
            if source.checksum not in ("SKIP", source.checksum):
                raise BuildError(
                    f"Invalid checksum for source file {source.url}:\n"
                    f"  expected {source.checksum}\n"
                    f"  actual   {file_sha}"
                )

            # Automatically extract source archives
            if not source.noextract:
                if not util.auto_extract(local_path, src_dir):
                    self.adapter.debug(
                        "Not extracting %s (unsupported archive type)",
                        local_path,
                    )

    def _prepare(self, recipe: Recipe, src_dir: str) -> None:
        """Prepare source files before building."""
        script = recipe.functions["prepare"]

        if not script:
            self.adapter.debug("Skipping prepare (nothing to do)")
            return

        self.adapter.info("Preparing source files")
        logs = bash.run_script(
            script=script,
            variables={
                **recipe.variables,
                **recipe.custom_variables,
                "srcdir": src_dir,
            },
        )

        self._print_logs(logs, "prepare()")

    def _build(self, recipe: Recipe, src_dir: str) -> None:
        """Build artifacts for a recipe."""
        script = recipe.functions["build"]

        if not script:
            self.adapter.debug("Skipping build (nothing to do)")
            return

        self.adapter.info("Building artifacts")

        # Set fixed atime and mtime for all the source files
        epoch = int(recipe.timestamp.timestamp())

        for filename in util.list_tree(src_dir):
            os.utime(filename, (epoch, epoch))

        mount_src = "/src"
        repo_src = "/repo"
        uid = os.getuid()
        pre_script: List[str] = []

        # Install required dependencies
        build_deps = []
        host_deps = []

        for dep in recipe.makedepends:
            if dep.kind == DependencyKind.Build:
                build_deps.append(dep.package)
            elif dep.kind == DependencyKind.Host:
                host_deps.append(dep.package)

        if build_deps:
            pre_script.extend(
                (
                    "export DEBIAN_FRONTEND=noninteractive",
                    "apt-get update -qq",
                    "apt-get install -qq --no-install-recommends"
                    ' -o Dpkg::Options::="--force-confdef"'
                    ' -o Dpkg::Options::="--force-confold"'
                    " -- " + " ".join(build_deps),
                )
            )

        if host_deps:
            opkg_conf_path = "$SYSROOT/etc/opkg/opkg.conf"
            pre_script.extend(
                (
                    'echo -n "dest root /',
                    "arch all 100",
                    "arch armv7-3.2 160",
                    "src/gz entware https://bin.entware.net/armv7sf-k3.2",
                    "arch rmall 200",
                    "src/gz toltec-rmall file:///repo/rmall",
                    f'" > "{opkg_conf_path}"',
                )
            )

            if recipe.arch != "rmall":
                pre_script.extend(
                    (
                        f'echo -n "arch {recipe.arch} 250',
                        f"src/gz toltec-{recipe.arch} file:///repo/{recipe.arch}",
                        f'" >> "{opkg_conf_path}"',
                    )
                )

            pre_script.extend(
                (
                    "opkg update --verbosity=0",
                    "opkg install --verbosity=0 --no-install-recommends"
                    " -- " + " ".join(host_deps),
                )
            )

        logs = bash.run_script_in_container(
            self.docker,
            image=self.IMAGE_PREFIX + recipe.image,
            mounts=[
                docker.types.Mount(
                    type="bind",
                    source=os.path.abspath(src_dir),
                    target=mount_src,
                ),
                docker.types.Mount(
                    type="bind",
                    source=os.path.abspath(self.repo_dir),
                    target=repo_src,
                ),
            ],
            variables={
                **recipe.variables,
                **recipe.custom_variables,
                "srcdir": mount_src,
            },
            script="\n".join(
                (
                    *pre_script,
                    f'cd "{mount_src}"',
                    script,
                    f'chown -R {uid}:{uid} "{mount_src}"',
                )
            ),
        )

        self._print_logs(logs, "build()")

    def _postprocessing(self, recipe: Recipe, src_dir: str) -> None:
        """Perform binary post-processing tasks such as stripping."""
        if (
            recipe.flags & BuildFlags.NOSTRIP
            and not recipe.flags & BuildFlags.PATCH_RM2FB
        ):
            self.adapter.debug("Skipping post-processing (nothing to do)")
            return

        self.adapter.info("Post-processing binaries")

        # Search for candidates
        cand = self._postprocessing_candidates(src_dir)

        # Save original mtimes to restore them afterwards
        # This will prevent any Makefile rules to be triggered again
        # in packaging scripts that use `make install`
        original_mtime = {}

        for file_path in (file for file_list in cand for file in file_list):
            original_mtime[file_path] = os.stat(file_path).st_mtime_ns

        script = []
        mount_src = "/src"

        # pylint: disable-next=unnecessary-lambda-assignment
        docker_file_path = lambda file_path: shlex.quote(
            os.path.join(mount_src, os.path.relpath(file_path, src_dir))
        )

        # Strip debugging symbols and unneeded sections
        if not recipe.flags & BuildFlags.NOSTRIP:
            if cand.strip_x86:
                script.append(
                    "strip --strip-all -- "
                    + " ".join(
                        docker_file_path(file_path) for file_path in cand.strip_x86
                    )
                )

                self.adapter.debug("x86 binaries to be stripped:")

                for file_path in cand.strip_x86:
                    self.adapter.debug(
                        " - %s",
                        os.path.relpath(file_path, src_dir),
                    )

            if cand.strip_arm:
                script.append(
                    '"${CROSS_COMPILE}strip" --strip-all -- '
                    + " ".join(
                        docker_file_path(file_path) for file_path in cand.strip_arm
                    )
                )

                self.adapter.debug("ARM binaries to be stripped:")

                for file_path in cand.strip_arm:
                    self.adapter.debug(
                        " - %s",
                        os.path.relpath(file_path, src_dir),
                    )

        # Add a dynamic dependency on the rm2fb client shim
        if recipe.flags & BuildFlags.PATCH_RM2FB and cand.patch_rm2fb:
            script = (
                [
                    "export DEBIAN_FRONTEND=noninteractive",
                    "apt-get update -qq",
                    "apt-get install -qq --no-install-recommends patchelf",
                ]
                + script
                + [
                    "patchelf --add-needed librm2fb_client.so.1 "
                    + " ".join(
                        docker_file_path(file_path) for file_path in cand.patch_rm2fb
                    )
                ]
            )

            self.adapter.debug("Binaries to be patched with rm2fb client:")

            for file_path in cand.patch_rm2fb:
                self.adapter.debug(
                    " - %s",
                    os.path.relpath(file_path, src_dir),
                )

        if script:
            logs = bash.run_script_in_container(
                self.docker,
                image=self.IMAGE_PREFIX + self.DEFAULT_IMAGE,
                mounts=[
                    docker.types.Mount(
                        type="bind",
                        source=os.path.abspath(src_dir),
                        target=mount_src,
                    )
                ],
                variables={},
                script="\n".join(script),
            )

            self._print_logs(logs)

        # Restore original mtimes
        for file_path, mtime in original_mtime.items():
            os.utime(file_path, ns=(mtime, mtime))

    @staticmethod
    def _postprocessing_candidates(src_dir: str) -> PostprocessingCandidates:
        """Search for binaries that need to be post-processed."""
        strip_arm = []
        strip_x86 = []
        patch_rm2fb = []

        for directory, _, files in os.walk(src_dir):
            for file_name in files:
                file_path = os.path.join(directory, file_name)

                try:
                    with open(file_path, "rb") as file:
                        info = ELFFile(file)
                        symtab = info.get_section_by_name(".symtab")

                        if info.get_machine_arch() == "ARM":
                            if symtab:
                                strip_arm.append(file_path)

                            dynamic = info.get_section_by_name(".dynamic")
                            rodata = info.get_section_by_name(".rodata")

                            if (
                                dynamic
                                and rodata
                                and rodata.data().find(b"/dev/fb0") != -1
                            ):
                                patch_rm2fb.append(file_path)
                        elif info.get_machine_arch() in ("x86", "x64") and symtab:
                            strip_x86.append(file_path)
                except ELFError:
                    # Ignore non-ELF files
                    pass
                except IsADirectoryError:
                    # Ignore directories
                    pass

        return PostprocessingCandidates(
            strip_arm=strip_arm,
            strip_x86=strip_x86,
            patch_rm2fb=patch_rm2fb,
        )

    def _package(self, package: Package, src_dir: str, pkg_dir: str) -> None:
        """Make a package from a recipe’s build artifacts."""
        self.adapter.info("Packaging build artifacts")
        logs = bash.run_script(
            script=package.functions["package"],
            variables={
                **package.variables,
                **package.custom_variables,
                "srcdir": src_dir,
                "pkgdir": pkg_dir,
            },
        )

        self._print_logs(logs, "package()")
        self.adapter.debug("Resulting tree:")

        for filename in util.list_tree(pkg_dir):
            self.adapter.debug(
                " - %s",
                os.path.normpath(os.path.join("/", os.path.relpath(filename, pkg_dir))),
            )

    def _archive(self, package: Package, pkg_dir: str) -> None:
        """Create an archive for a package."""
        self.adapter.info("Creating archive")
        ar_path = os.path.join(paths.REPO_DIR, package.filename())
        ar_dir = os.path.dirname(ar_path)
        os.makedirs(ar_dir, exist_ok=True)

        # Inject Oxide-specific hook for reloading apps
        if os.path.exists(os.path.join(pkg_dir, "opt/usr/share/applications")):
            oxide_hook = "\nreload-oxide-apps\n"
            package.functions["configure"] += oxide_hook
            package.functions["postupgrade"] += oxide_hook
            package.functions["postremove"] += oxide_hook

        # Convert install scripts to Debian format
        scripts = {}
        script_header = "\n".join(
            (
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    set -euo pipefail
                    """
                ),
                bash.put_variables(
                    {
                        **package.variables,
                        **package.custom_variables,
                    }
                ),
                bash.put_functions(package.custom_functions),
                self.install_lib,
            )
        )

        for name, script, action in (
            ("preinstall", "preinst", "install"),
            ("configure", "postinst", "configure"),
        ):
            if package.functions[name]:
                scripts[script] = "\n".join(
                    (
                        script_header,
                        textwrap.dedent(
                            f"""\
                            if [[ $1 = {action} ]]; then
                                script() {{
                            """
                        ),
                        package.functions[name],
                        textwrap.dedent(
                            """\
                                }
                                script
                            fi
                            """
                        ),
                    )
                )

        for step in ("pre", "post"):
            if (
                package.functions[step + "upgrade"]
                or package.functions[step + "remove"]
            ):
                script = script_header

                for action in ("upgrade", "remove"):
                    if package.functions[step + action]:
                        script += "\n".join(
                            (
                                textwrap.dedent(
                                    f"""\
                                    if [[ $1 = {action} ]]; then
                                        script() {{
                                    """
                                ),
                                package.functions[step + action],
                                textwrap.dedent(
                                    """\
                                        }
                                        script
                                    fi
                                    """
                                ),
                            )
                        )

                scripts[step + "rm"] = script

        self.adapter.debug("Install scripts:")

        if scripts:
            for script in sorted(scripts):
                self.adapter.debug(" - %s", script)
        else:
            self.adapter.debug("(none)")

        epoch = int(package.parent.timestamp.timestamp())

        with open(ar_path, "wb") as file:
            ipk.make_ipk(
                file,
                epoch=epoch,
                pkg_dir=pkg_dir,
                metadata=package.control_fields(),
                scripts=scripts,
            )

        # Set fixed atime and mtime for the resulting archive
        os.utime(ar_path, (epoch, epoch))

    def _print_logs(
        self,
        logs: bash.LogGenerator,
        function_name: str = None,
        max_lines_on_fail: int = 50,
    ) -> None:
        """
        Print logs to the debug output or buffer and print the last n log lines
        if a ScriptError is caught.

        :param logs: generator of log lines
        :param function_name: calling function name
        :param max_lines_on_fail: number of context lines to print
            in non-debug mode
        """
        log_buffer: Deque[str] = deque()
        try:
            for line in logs:
                if self.adapter.getEffectiveLevel() <= logging.DEBUG:
                    self.adapter.debug(line)
                else:
                    if len(log_buffer) == max_lines_on_fail:
                        log_buffer.popleft()
                    log_buffer.append(line)
        except bash.ScriptError as err:
            if len(log_buffer) > 0:
                self.adapter.info(
                    f"Only showing up to {max_lines_on_fail} lines of context. "
                    + "Use --verbose for the full output."
                )
                for line in log_buffer:
                    self.adapter.error(line)

            if function_name:
                self.adapter.error(f"{function_name} failed")

            raise err
