# Essential build tools and cross-compiling build tools
FROM debian:buster

RUN apt-get update -q && apt-get install -yq \
        build-essential \
        cmake \
        crossbuild-essential-armhf \
        curl \
        git \
        python \
        python3 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update -q && apt-get install -yq \
        python-pip \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install okp
