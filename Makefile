# Copyright (c) 2020 The Toltec Contributors
# SPDX-License-Identifier: MIT

HOST?=10.11.99.1
RECIPES=$(shell ls package/)
RECIPES_PUSH=$(foreach app, $(RECIPES), $(app)-push)
RECIPES_CLEAN=$(foreach app, $(RECIPES), $(app)-clean)

ifeq ($(RUNNER_DEBUG), 1)
FLAGS+= --verbose
endif

define USAGE
Building packages:

    repo            Build the repository and reuse archives from the remote
                    repository for existing package versions.
    repo-local      Build the repository without using existing archives from
                    the remote repository.
    repo-new        Build only the new packages in the repository based
                    on what exists in the remote repository.
    RECIPE          Build packages from the given recipe.
    push            Push all built packages to the .cache/toltec directory
                    on the reMarkable. Requires `rsync` on the reMarkable, which
                    can be installed with `opkg install rsync`.
    RECIPE-push     Push built packages from the given recipe to the
                    .cache/toltec directory on the reMarkable. Requires `rsync`
                    on the reMarkable, which can be installed with
                    `opkg install rsync`.

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

.venv/bin/activate: requirements.txt
	@echo "Setting up development virtual env in .venv"
	python -m venv .venv; \
	. .venv/bin/activate; \
	python -m pip install -r requirements.txt

repo: .venv/bin/activate
	. .venv/bin/activate; \
	./scripts/repo_build.py $(FLAGS)

repo-local: .venv/bin/activate
	. .venv/bin/activate; \
	./scripts/repo_build.py --local $(FLAGS)

repo-new: .venv/bin/activate
	. .venv/bin/activate; \
	./scripts/repo_build.py --diff $(FLAGS)

repo-check: .venv/bin/activate
	. .venv/bin/activate; \
	./scripts/repo-check build/repo

$(RECIPES): %: .venv/bin/activate
	. .venv/bin/activate; \
	./scripts/package_build.py $(FLAGS) "$(@)"

push: %:
	if ! rsync --rsync-path /opt/bin/rsync \
	      --archive --verbose --compress --delete \
	      build/repo/ \
	      root@"$(HOST)":~/.cache/toltec/; then \
		echo "rysnc exited with an error." \
	         "Make sure rsync is installed on your reMarkable."; \
	fi

$(RECIPES_PUSH): SHELL:=/bin/bash
$(RECIPES_PUSH): %:
	source package/$(@:%-push=%)/package; \
	if ! rsync --rsync-path /opt/bin/rsync \
	      --archive --verbose --compress --ignore-times \
	      $$(for pkg in $${pkgnames[@]}; do \
	             echo build/repo/*/"$$pkg"_*.ipk; \
	         done) \
	      root@"$(HOST)":~/.cache/toltec/; then \
		echo "rysnc exited with an error." \
	         "Make sure rsync is installed on your reMarkable."; \
	fi

format: .venv/bin/activate
	@echo "==> Checking Bash formatting"
	shfmt -d .
	@echo "==> Checking Python formatting"
	. .venv/bin/activate; \
	black --line-length 80 --check --diff scripts

format-fix: .venv/bin/activate
	@echo "==> Fixing Bash formatting"
	shfmt -l -w .
	@echo "==> Fixing Python formatting"
	. .venv/bin/activate; \
	black --line-length 80 scripts

lint: .venv/bin/activate
	@echo "==> Linting Bash scripts"
# 	shellcheck $$(shfmt -f .) -P SCRIPTDIR
	@echo "==> Typechecking Python files"
	. .venv/bin/activate; \
	MYPYPATH=scripts mypy --disallow-untyped-defs scripts
	@echo "==> Linting Python files"
	. .venv/bin/activate; \
	PYTHONPATH=: pylint scripts

$(RECIPES_CLEAN): %:
	rm -rf build/package/"$(@:%-clean=%)"

clean:
	rm -rf build

.PHONY: \
    help \
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
