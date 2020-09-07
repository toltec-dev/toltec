# Essential cross-compiling build tools for the reMarkable
FROM debian:buster

# Install common building tools
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Fetch crosstool-ng sources
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends git \
    && cd /root \
    && git clone https://github.com/crosstool-ng/crosstool-ng \
    && cd crosstool-ng \
    && git checkout crosstool-ng-1.24.0 \
    && apt-get autoremove -y git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add configuration for the reMarkable
COPY arm-remarkable-linux-gnueabihf /root/crosstool-ng/samples/arm-remarkable-linux-gnueabihf

# Build the toolchain
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -y \
    && apt-get install -y \
        autoconf \
        bison \
        file \
        flex \
        gawk \
        help2man \
        libncurses-dev \
        libtool-bin \
        texinfo \
        unzip \
    && cd /root/crosstool-ng \
    && ./bootstrap \
    && ./configure --enable-local \
    && make \
    # Root folder in which the cross-compiling toolchain will be placed
    && export CT_PREFIX="/opt/x-tools" \
    && ./ct-ng arm-remarkable-linux-gnueabihf \
    && ./ct-ng build \
    && cd .. \
    && rm -rf crosstool-ng \
    && apt-get autoremove -y git \
    && apt-get autoremove -yq \
        autoconf \
        bison \
        file \
        flex \
        gawk \
        help2man \
        libncurses-dev \
        libtool-bin \
        texinfo \
        unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add cross-compiling tools to PATH
ENV PATH="$PATH:/opt/x-tools/arm-remarkable-linux-gnueabihf/bin"
