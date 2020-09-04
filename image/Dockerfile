FROM debian:buster

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

# Add rust nightly with armv7 target
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
    | sh -s -- --default-toolchain nightly --target armv7-unknown-linux-gnueabihf --profile minimal -y -q
ENV PATH="$PATH:/root/.cargo/bin"

# Install opkg-utils
RUN git clone git://git.yoctoproject.org/opkg-utils /opkg-utils \
    && cd /opkg-utils \
    && git checkout 0.4.3 \
    && ln -s /opkg-utils/opkg-make-index /usr/local/bin
