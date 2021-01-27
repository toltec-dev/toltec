# Copyright (c) 2020 The Toltec Contributors
# SPDX-License-Identifier: MIT

HOST?=10.11.99.1
RECIPES=$(shell ls package/)
RECIPES_PUSH=$(foreach app, $(RECIPES), $(app)-push)
RECIPES_CLEAN=$(foreach app, $(RECIPES), $(app)-clean)

define USAGE
Building packages:

    repo            Build the repository and reuse archives from the remote
                    repository for existing package versions.
    repo-local      Build the repository without using existing archives from
                    the remote repository.
    repo-new        Build only the new packages in the repository based
                    on what exists in the remote repository.
    RECIPE          Build packages from the given recipe.
    RECIPE-push     Push built packages from the given recipe to the
                    .cache/opkg directory on the reMarkable.

Building webpages:

    web             Generate the Toltec website.

Checking for errors:

    repo-check      Compare the local repository to the remote one.
    format          Check that the source code formatting follows
                    the style guide.
    format-fix      Automatically reformat the source code to follow
                    the style guide.
    lint            Perform static analysis on the source code to find
                    erroneous constructs.

Housekeeping:

    RECIPE-clean    Remove build artifacts from a given recipe.
    clean           Remove all build artifacts.
endef
export USAGE

help:
	@echo "$$USAGE"

web:
	./scripts/web-build web build/web

repo:
	./scripts/repo_build.py $(FLAGS)

repo-local:
	./scripts/repo_build.py --local $(FLAGS)

repo-new:
	./scripts/repo_build.py --diff $(FLAGS)

repo-check:
	./scripts/repo-check build/repo

$(RECIPES): %:
	./scripts/package_build.py $(FLAGS) "$(@)"

push: %:
	rsync --rsync-path /opt/bin/rsync \
	      --archive --verbose --compress --delete \
	      build/repo/ \
	      root@"$(HOST)":~/.cache/toltec/

format:
	@echo "==> Checking Bash formatting"
	shfmt -d .
	@echo "==> Checking Python formatting"
	black --line-length 80 --check --diff scripts

format-fix:
	@echo "==> Fixing Bash formatting"
	shfmt -l -w .
	@echo "==> Fixing Python formatting"
	black --line-length 80 scripts

lint:
	@echo "==> Linting Bash scripts"
	shellcheck $$(shfmt -f .)
	@echo "==> Typechecking Python files"
	MYPYPATH=scripts mypy --disallow-untyped-defs scripts
	@echo "==> Linting Python files"
	PYTHONPATH=: pylint scripts
	@echo "==> Verifying that the bootstrap checksum is correct"
	./scripts/bootstrap/checksum-check

$(RECIPES_CLEAN): %:
	rm -rf build/package/"$(@:%-clean=%)"

clean:
	rm -rf build

.PHONY: \
    help \
    web \
    repo \
    repo-local \
    repo-check \
    $(RECIPES) \
    $(RECIPES_PUSH) \
    format \
    format-fix \
    lint \
    $(RECIPES_CLEAN) \
    clean
