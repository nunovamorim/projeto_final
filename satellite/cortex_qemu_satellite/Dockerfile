# Use an official embedded systems development image
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        wget \
        gcc-arm-none-eabi \
        qemu-system-arm \
        python3 \
        python3-pip \
        cmake \
        ninja-build \
        && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /satellite

# Copy the project files
COPY . /satellite/

# Set environment variables
ENV PATH="/satellite:${PATH}"

# Build command (will be executed when container is run)
CMD ["bash", "-c", "cd /satellite && chmod +x build_and_run.sh && ./build_and_run.sh"]
