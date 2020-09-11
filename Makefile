HOST?=10.11.99.1
PACKAGES=$(shell ls package/)
PUSH_PACKAGES=$(foreach app, $(PACKAGES), push-$(app))

define USAGE
Available targets:

    repo            Build the repository and reuse archives from the remote
                    repository for existing package versions.
    force-repo      Build the repository without reusing existing archives.
    check           Compare the local repository to the remote one.
    RECIPE          Build any package individually.
    push-RECIPE     Push any built package to .cache/opkg on the reMarkable.
                    (Plug in your reMarkable first!)
    images          Build the Docker images while reusing the remote cache
                    when possible.

Where RECIPE is one of the following available recipes:

${PACKAGES}
endef
export USAGE

help:
	@echo "$$USAGE"

repo:
	rm build/repo -fr
	./scripts/build-repo package build

force-repo:
	rm build/repo -fr
	./scripts/build-repo -f package build

check:
	./scripts/check-repo build/repo

$(PACKAGES): %:
	rm build/packages/"${@}" -fr
	./scripts/build-package package/"${@}" build/packages/"${@}"

$(PUSH_PACKAGES): %:
	ssh root@"${HOST}" mkdir -p .cache/opkg
	scp build/packages/"$(@:push-%=%)"/*.ipk root@"${HOST}":.cache/opkg

images:
	./scripts/build-images image

.PHONY: help repo check $(PACKAGES) $(PUSH_PACKAGES)
