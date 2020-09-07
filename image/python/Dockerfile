# Python distribution
ARG BASE
FROM $BASE

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -y \
    && cd /root \
    && apt-get install -y \
        python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
