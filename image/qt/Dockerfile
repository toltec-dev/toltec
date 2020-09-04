# Qt5 using the armv7-hf cross-compiler
ARG BASE
FROM $BASE

RUN apt-get update -q && apt-get install -yq \
    qt5-default \
    && rm -rf /var/lib/apt/lists/*
