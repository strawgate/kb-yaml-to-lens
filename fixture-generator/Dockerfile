# Dockerfile for Kibana Lens Fixture Generator
# This tool generates test fixtures using Kibana's official LensConfigBuilder API

FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x (match Kibana's .node-version)
ARG NODE_VERSION=20.19.4
RUN curl -fsSL https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz | \
    tar -xJ -C /usr/local --strip-components=1

# Install Yarn Classic
RUN npm install -g yarn@1.22.19

# Set heap size for large builds
ENV NODE_OPTIONS="--max_old_space_size=8192"

# Clone Kibana main branch (shallow clone for speed)
WORKDIR /kibana
RUN git clone --depth 1 --branch main https://github.com/elastic/kibana.git .

# Run bootstrap (this takes 15-30 minutes)
RUN yarn kbn bootstrap

# Create tool directories
WORKDIR /tool
RUN mkdir -p /tool/input /tool/output

# Copy tool source files
COPY src/ /tool/src/
COPY package.json /tool/
COPY tsconfig.json /tool/

# Install tool dependencies
RUN yarn install

# Entry point
ENTRYPOINT ["node", "/tool/src/cli.js"]
CMD ["--help"]
