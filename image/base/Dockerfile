# Essential build tools and cross-compiling build tools
FROM debian:stretch

RUN apt-get update -q && apt-get install -yq \
        build-essential \
        cmake \
        crossbuild-essential-armhf \
        curl \
        git \
        python \
        python3 \
    && rm -rf /var/lib/apt/lists/*
