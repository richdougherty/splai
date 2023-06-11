# Stage 1: Build stage
FROM docker.io/library/ubuntu:22.04

# Update the system and install dependencies
RUN export DEBIAN_FRONTEND noninteractive && \
    apt-get update && \
    apt-get install -y \
        sudo \
        git \
        python3.10 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip to avoid AssertionError (https://github.com/pypa/pip/issues/10851)
RUN pip3 install --no-cache-dir --no-warn-script-location --upgrade pip

# Change to a non-root user
RUN useradd --uid 1001 devuser --gid users --groups sudo --create-home --shell /usr/bin/bash --no-log-init
USER devuser
WORKDIR /home/devuser

# Install Python requirements
ENV PATH=/root/.local/bin:$PATH
COPY requirements.txt /tmp
RUN pip3 install --no-cache-dir --user -r /tmp/requirements.txt
