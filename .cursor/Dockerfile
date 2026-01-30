# Cursor Cloud Agents Development Environment
#
# This Dockerfile is used by Cursor Cloud Agents via environment.json.
# It creates a development environment for the kb-yaml-to-lens project,
# supporting both the Python compiler and TypeScript VS Code extension.

FROM ubuntu:24.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install system packages
RUN apt-get update && apt-get install -y \
    # Build essentials
    build-essential \
    make \
    sudo \
    # Python 3.12
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    # Git and utilities
    git \
    curl \
    wget \
    ca-certificates \
    gnupg \
    # For VS Code extension E2E tests (virtual display)
    xvfb \
    x11-utils \
    libgtk-3-0 \
    libgbm1 \
    libnss3 \
    libasound2t64 \
    libxss1 \
    libsecret-1-0 \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager)
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /usr/local/bin/

# Install global npm packages
RUN npm install -g markdownlint-cli

# Verify installations
RUN python --version && \
    node --version && \
    npm --version && \
    uv --version && \
    make --version && \
    git --version

# Set working directory
WORKDIR /workspace

# Default shell
CMD ["/bin/bash"]
