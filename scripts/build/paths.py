# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Well-known paths for Toltec."""

import os

# Root directory where this clone of the Toltec repo lives
GIT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Directory where the tooling scripts are stored
SCRIPTS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

# Directory where recipes can be found
RECIPE_DIR = os.path.join(GIT_DIR, "package")

# Working directory for building recipes
WORK_DIR = os.path.join(GIT_DIR, "build", "package")

# Directory used for storing built packages
REPO_DIR = os.path.join(GIT_DIR, "build", "repo")
