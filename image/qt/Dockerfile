# Qt5 using the armv7-hf cross-compiler
ARG REPOSITORY
ARG BRANCH
FROM docker.pkg.github.com/$REPOSITORY/base:$BRANCH

RUN apt-get update -q && apt-get install -yq \
    qt5-default \
    && rm -rf /var/lib/apt/lists/*
