PACKAGE?=draft

default: repo
repo:
	docker build --tag toltec:base . -f image/Dockerfile
	docker build --tag toltec:build . -f image/Dockerfile.build
	bash scripts/build-repo-in-docker

package:
	docker build --tag toltec:base . -f image/Dockerfile
	docker build --tag toltec:build . -f image/Dockerfile.build
	echo "BUILDING ${PACKAGE}"
	PACKAGE=${PACKAGE} bash scripts/build-package-in-docker



.PHONY: docker package

