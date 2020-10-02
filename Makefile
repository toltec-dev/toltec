HOST?=10.11.99.1
PACKAGES=$(shell ls package/)
PUSH_PACKAGES=$(foreach app, $(PACKAGES), $(app)-push)

define USAGE
Available targets:

    repo            Build the repository and reuse archives from the remote
                    repository for existing package versions.
    repo-local      Build the repository without using existing archives from
		    the remote repository.
    repo-check      Compare the local repository to the remote one.
    RECIPE          Build any package individually.
    RECIPE-push     Push any built package to .cache/opkg on the reMarkable.
                    (Plug in your reMarkable first!)
    clean           Remove all build artifacts.

Where RECIPE is one of the following available recipes:

${PACKAGES}
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

clean:
	rm -rf build

.PHONY: help repo repo-local repo-check $(PACKAGES) $(PUSH_PACKAGES) clean
