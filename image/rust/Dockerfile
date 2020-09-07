# Rust nightly targeting the armv7-hf architecture
ARG BASE
FROM $BASE

# Install rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y -q \
    --default-toolchain nightly \
    --target armv7-unknown-linux-gnueabihf \
    --profile minimal

# Add rust binaries to PATH
ENV PATH="$PATH:/root/.cargo/bin"

# Target reMarkable architecture by default
COPY config /root/.cargo/config
