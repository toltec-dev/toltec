# Python distribution
ARG BASE
FROM $BASE

RUN apt-get update -q && apt-get install -yq \
        python-pip \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*
