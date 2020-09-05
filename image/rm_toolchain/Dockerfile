FROM debian:buster

RUN apt-get update -q && apt-get install -yq \
    build-essential \
    gcc-arm-linux-gnueabihf \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update -q && apt-get install -yq \
    && rm -rf /var/lib/apt/lists/*

# Download dependencies
RUN apt-get update -q && apt-get install -yq \
    build-essential \
    bsdtar \
    curl \
    git \
    openssh-client \
    python3 \
    rsync \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Download and install the reMarkable build toolchain
RUN curl https://remarkable.engineering/oecore-x86_64-cortexa9hf-neon-toolchain-zero-gravitas-1.8-23.9.2019.sh -o install-toolchain.sh \
    && chmod u+x install-toolchain.sh \
    && ./install-toolchain.sh \
    && rm install-toolchain.sh

# Add missing CMake toolchain file to toolchain
RUN mkdir -p /usr/local/oecore-x86_64/sysroots/x86_64-oesdk-linux/usr/share/cmake \
    && curl https://raw.githubusercontent.com/openembedded/openembedded-core/uninative-2.9/meta/recipes-devtools/cmake/cmake/OEToolchainConfig.cmake -o /usr/local/oecore-x86_64/sysroots/x86_64-oesdk-linux/usr/share/cmake/OEToolchainConfig.cmake

