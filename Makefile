PACKAGE?=draft
HOST?=10.11.99.1

default: repo
repo: docker_images
	bash scripts/build-repo-in-docker

# Use `make <app>` to build any package individually
# Use `make push_<app>` to push any package to .cache/opkg/ on the rM
PACKAGES=$(shell ls package/)
PUSH_PACKAGES=$(foreach app, $(PACKAGES), push_$(app))

$(PACKAGES): %:
	PACKAGE=$(@) make package

$(PUSH_PACKAGES): %:
	PACKAGE=$(@:push_%=%) make push_package

package: docker_images
	echo "BUILDING ${PACKAGE}"
	PACKAGE=${PACKAGE} bash scripts/build-package-in-docker

push_package:
	ssh root@${HOST} mkdir -p .cache/opkg/
	PACKAGE=${PACKAGE} scp artifacts/package/${PACKAGE}/*.ipk root@${HOST}:.cache/opkg/

docker_images:
	docker build --tag toltec:base . -f image/base/Dockerfile
	docker build --tag toltec:rm . -f image/rm_toolchain/Dockerfile --build-arg "BASE=toltec:base"
	docker build --tag toltec:build . -f image/build/Dockerfile

.PHONY: docker package

