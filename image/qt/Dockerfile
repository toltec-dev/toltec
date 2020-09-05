# Full Qt toolchain for the reMarkable
ARG BASE
FROM $BASE

# Build Qt from source targeting armhf
RUN cd /root \
    && git clone https://code.qt.io/qt/qt5.git \
    && cd qt5 \
    && git checkout v5.11.3 \
    && perl init-repository --module-subset=default,-qtwebengine \
    && cp -R qtbase/mkspecs/linux-arm-gnueabi-g++ \
             qtbase/mkspecs/linux-arm-gnueabihf-g++ \
    && sed -i 's/arm-linux-gnueabi-/arm-linux-gnueabihf-/' \
              qtbase/mkspecs/linux-arm-gnueabihf-g++/qmake.conf \
    && cd .. \
    && mkdir qt5-build \
    && cd qt5-build \
    && ../qt5/configure \
        -confirm-license \
        -prefix /usr \
        -opensource \
        -nomake examples \
        -nomake tests  \
        -no-opengl \
        -xplatform linux-arm-gnueabihf-g++ \
        -platform linux-g++ \
        -reduce-exports \
    && make \
    && make install \
    && cd .. \
    && rm -rf qt5 qt5-build

# Add the closed-source libqsgepaper library
RUN curl https://toltec.delab.re/thirdparty/lib/libqsgepaper.a -o /usr/lib/libqsgepaper.a \
    && curl https://toltec.delab.re/thirdparty/include/epframebuffer.h -o /usr/include/epframebuffer.h
