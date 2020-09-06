PACKAGE?=draft
HOST?=10.11.99.1
BRANCH=$(shell git rev-parse --abbrev-ref HEAD)

default: repo
repo:
	bash scripts/build-repo-in-docker

# Use `make <app>` to build any package individually
# Use `make push_<app>` to push any package to .cache/opkg/ on the rM
PACKAGES=$(shell ls package/)
IMAGES=$(shell ls image/)
PUSH_PACKAGES=$(foreach app, $(PACKAGES), push_$(app))
BUILD_IMAGES=$(foreach image, $(IMAGES), docker_build_$(image))

$(PACKAGES): %:
	PACKAGE=$(@) make package

$(PUSH_PACKAGES): %:
	PACKAGE=$(@:push_%=%) make push_package

package:
	bash scripts/build-docker-and-package ${PACKAGE}

push_package:
	ssh root@${HOST} mkdir -p .cache/opkg/
	PACKAGE=${PACKAGE} scp artifacts/package/${PACKAGE}/*.ipk root@${HOST}:.cache/opkg/

# TODO: support multiple levels of base images,
# right now, the base image is hardcoded to toltec/base:${BRANCH}
$(BUILD_IMAGES): %:
	docker build --tag toltec/${@:docker_build_%=%}:${BRANCH} . -f image/${@:docker_build_%=%}/Dockerfile --build-arg BASE=toltec/base:${BRANCH}

.PHONY: package push_package

