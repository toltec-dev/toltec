PACKAGE?=draft
HOST?=10.11.99.1

default: repo
repo:
	docker build --tag toltec:base . -f image/Dockerfile
	docker build --tag toltec:build . -f image/Dockerfile.build
	bash scripts/build-repo-in-docker

# Use `make <app>` to build any package individually
# Use `make push_<app>` to push any package to .cache/opkg/ on the rM
PACKAGES=$(shell ls package/)
PUSH_PACKAGES=$(foreach app, $(PACKAGES), push_$(app))

$(PACKAGES): %:
	PACKAGE=$(@) make package

$(PUSH_PACKAGES): %:
	PACKAGE=$(@:push_%=%) make push_package

package:
	docker build --tag toltec:base . -f image/Dockerfile
	docker build --tag toltec:build . -f image/Dockerfile.build
	echo "BUILDING ${PACKAGE}"
	PACKAGE=${PACKAGE} bash scripts/build-package-in-docker

push_package:
	ssh root@${HOST} mkdir -p .cache/opkg/
	PACKAGE=${PACKAGE} scp artifacts/package/${PACKAGE}/*.ipk root@${HOST}:.cache/opkg/

.PHONY: docker package

