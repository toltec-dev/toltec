# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""
Load the Jinja2 templating engine.
"""
from jinja2 import Environment, PackageLoader

env = Environment(
    loader=PackageLoader("toltec", "templates"),
    autoescape=True,
)
