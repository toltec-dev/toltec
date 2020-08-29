FROM debian:buster

# Download dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    bsdtar \
    curl \
    python3 \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Download and install the reMarkable build toolchain
RUN curl https://remarkable.engineering/oecore-x86_64-cortexa9hf-neon-toolchain-zero-gravitas-1.8-23.9.2019.sh -o install-toolchain.sh \
    && chmod u+x install-toolchain.sh \
    && ./install-toolchain.sh \
    && rm install-toolchain.sh

# Add missing CMake toolchain file
RUN curl https://raw.githubusercontent.com/openembedded/openembedded-core/master/meta/recipes-devtools/cmake/cmake/OEToolchainConfig.cmake -o OEToolchainConfig.cmake \
    && mkdir -p /usr/local/oecore-x86_64/sysroots/x86_64-oesdk-linux/usr/share/cmake \
    && mv OEToolchainConfig.cmake /usr/local/oecore-x86_64/sysroots/x86_64-oesdk-linux/usr/share/cmake
