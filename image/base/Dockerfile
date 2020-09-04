FROM debian:stretch

RUN apt-get update -q && apt-get install -yq \
    build-essential \
    gcc-arm-linux-gnueabihf \
    curl \
    && rm -rf /var/lib/apt/lists/*
