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
    RECIPE          Build packages from the given recipe.
    RECIPE-push     Push built packages from the given recipe to the
                    .cache/opkg directory on the reMarkable.

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

repo:
	./scripts/repo-build package build/package build/repo "$$remote_repo"

repo-local:
	./scripts/repo-build -l package build/package build/repo "$$remote_repo"

repo-check:
	./scripts/repo-check build/repo

$(RECIPES): %:
	./scripts/package-build package/"${@}" build/package/"${@}"

$(RECIPES_PUSH): %:
	ssh root@"${HOST}" mkdir -p .cache/opkg
	scp build/package/"$(@:%-push=%)"/*/*.ipk root@"${HOST}":.cache/opkg

format:
	@echo "==> Checking the formatting of shell scripts"
	shfmt -d .

format-fix:
	@echo "==> Fixing the formatting of shell scripts"
	shfmt -l -w .

lint:
	@echo "==> Linting shell scripts"
	shellcheck $$(shfmt -f .)
	@echo "==> Verifying that the bootstrap checksum is correct"
	./scripts/bootstrap/checksum-check

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
