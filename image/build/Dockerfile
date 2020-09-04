FROM toltec:rm

RUN apt-get update -q && apt-get install -yq \
    bsdtar \
    build-essential \
    curl \
    g++-arm-linux-gnueabihf \
    gcc-arm-linux-gnueabihf \
    git \
    openssh-client \
    python3 \
    python3-pip \
    rsync \
    xz-utils \
    zip \
    && rm -rf /var/lib/apt/lists/* \
    && echo "done"

# Install opkg-utils
RUN git clone git://git.yoctoproject.org/opkg-utils /opkg-utils \
    && cd /opkg-utils \
    && git checkout 0.4.3 \
    && ln -s /opkg-utils/opkg-make-index /usr/local/bin

WORKDIR /toltec
COPY . /toltec/
