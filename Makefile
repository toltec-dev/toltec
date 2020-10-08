# Copyright (c) 2020 The Toltec Contributors
# SPDX-License-Identifier: MIT

HOST?=10.11.99.1
PACKAGES=$(shell ls package/)
PUSH_PACKAGES=$(foreach app, $(PACKAGES), $(app)-push)

define USAGE
Building packages:

    repo            Build the repository and reuse archives from the remote
                    repository for existing package versions.
    repo-local      Build the repository without using existing archives from
                    the remote repository.
    repo-check      Compare the local repository to the remote one.
    RECIPE          Build any package individually.
    RECIPE-push     Push any built package to .cache/opkg on the reMarkable.
                    (Plug in your reMarkable first!)

Checking for errors:

    format          Check that the source code formatting follows
                    the style guide.
    format-fix      Automatically reformat the source code to follow
                    the style guide.
    lint            Perform static analysis on the source code to find
                    erroneous constructs.

Housekeeping:

    clean           Remove all build artifacts.
endef
export USAGE

help:
	@echo "$$USAGE"

repo:
	./scripts/repo-build package build/packages build/repo

repo-local:
	./scripts/repo-build -l package build/packages build/repo

repo-check:
	./scripts/repo-check build/repo

$(PACKAGES): %:
	./scripts/package-build package/"${@}" build/packages

$(PUSH_PACKAGES): %:
	ssh root@"${HOST}" mkdir -p .cache/opkg
	scp build/packages/"$(@:%-push=%)"/*.ipk root@"${HOST}":.cache/opkg

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

clean:
	rm -rf build

.PHONY: \
    help \
    repo \
    repo-local \
    repo-check \
    $(PACKAGES) \
    $(PUSH_PACKAGES) \
    format \
    format-fix \
    lint \
    clean
