HOST?=10.11.99.1
PACKAGES=$(shell ls package/)
PUSH_PACKAGES=$(foreach app, $(PACKAGES), $(app)-push)

define USAGE
Available targets:

    repo            Build the repository and reuse archives from the remote
                    repository for existing package versions.
    repo-force      Build the repository without reusing existing archives.
    repo-check      Compare the local repository to the remote one.
    RECIPE          Build any package individually.
    RECIPE-push     Push any built package to .cache/opkg on the reMarkable.
                    (Plug in your reMarkable first!)

Where RECIPE is one of the following available recipes:

${PACKAGES}
endef
export USAGE

help:
	@echo "$$USAGE"

repo:
	rm -rf build
	./scripts/build-repo package build

repo-force:
	rm -rf build
	./scripts/build-repo -f package build

repo-check:
	./scripts/check-repo build/repo

$(PACKAGES): %:
	rm -rf build/packages/"${@}"
	./scripts/build-package package/"${@}" build/packages/"${@}"

$(PUSH_PACKAGES): %:
	ssh root@"${HOST}" mkdir -p .cache/opkg
	scp build/packages/"$(@:push-%=%)"/*.ipk root@"${HOST}":.cache/opkg

.PHONY: help repo repo-force repo-check $(PACKAGES) $(PUSH_PACKAGES)
