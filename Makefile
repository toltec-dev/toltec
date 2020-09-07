HOST?=10.11.99.1
PACKAGES=$(shell ls package/)
PUSH_PACKAGES=$(foreach app, $(PACKAGES), push-$(app))

help:
	@echo "Available recipes: ${PACKAGES}"
	@echo
	@echo "Use 'make repo' to build all the packages and the index file"
	@echo "Use 'make <recipe>' to build any package individually"
	@echo "Use 'make push-<recipe>' to push any built package to .cache/opkg on the reMarkable"

repo:
	./scripts/build-repo package build

$(PACKAGES): %:
	rm build/packages/"${@}" -fr
	./scripts/build-package package/"$(@)" build/packages/"$(@)"

$(PUSH_PACKAGES): %:
	ssh root@"${HOST}" mkdir -p .cache/opkg/
	scp build/packages/"$(@:push-%=%)"/*.ipk root@"${HOST}":.cache/opkg

.PHONY: help repo $(PACKAGES) $(PUSH_PACKAGES)
