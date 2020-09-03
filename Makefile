PACKAGE?=draft
HOST?=10.11.99.1

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

push_package:
	ssh root@${HOST} mkdir -p .config/opkg/
	PACKAGE=${PACKAGE} scp artifacts/package/${PACKAGE}/*.ipk root@${HOST}:.config/opkg/

.PHONY: docker package

