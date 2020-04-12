FROM fedora

RUN \
    dnf --assumeyes install \
        https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
        https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm && \
    dnf --assumeyes update && \
    dnf --assumeyes install \
        python3-pip \
        python3-devel \
        gcc \
        redhat-rpm-config \
        rocksdb-devel \
        gcc-c++ \
        lz4-devel \
        bzip2-devel \
        zlib-devel \
        snappy-devel && \
    dnf clean all

RUN \
    pip3 install pytest && \
    pip3 install aiohttp && \
    pip3 install aioredis && \
    pip3 install grpcio && \
    pip3 install msgpack-python && \
    pip3 install psutil && \
    pip3 install python-rocksdb && \
    pip3 install redis && \
    pip3 install protobuf && \
    pip3 install uvloop
