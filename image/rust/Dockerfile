# Rust nightly targeting the armv7-hf architecture
ARG BRANCH
ARG REPOSITORY
FROM docker.pkg.github.com/$REPOSITORY/base:$BRANCH

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y -q \
    --default-toolchain nightly \
    --target armv7-unknown-linux-gnueabihf \
    --profile minimal
ENV PATH="$PATH:/root/.cargo/bin"
