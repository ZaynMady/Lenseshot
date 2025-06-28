FROM jenkins/agent:alpine-jdk21

USER root

# Install dependencies for building Python
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    bzip2-dev \
    zlib-dev \
    xz-dev \
    wget \
    readline-dev \
    sqlite-dev \
    make \
    bash

# Download and compile Python 3.13
RUN wget https://www.python.org/ftp/python/3.13.5/Python-3.13.5.tgz && \
    tar -xf Python-3.13.5.tgz && \
    cd Python-3.13.5 && \
    ./configure --prefix=/usr/local --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.13.5 Python-3.13.5.tgz

# Optional: symlink python3 -> python3.13
RUN ln -s /usr/local/bin/python3.13 /usr/local/bin/python3 && \
    ln -s /usr/local/bin/pip3.13 /usr/local/bin/pip3

USER jenkins

# Confirm versions (optional for debugging)
# RUN python3 --version && pip3 --version
