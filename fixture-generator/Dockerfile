# Kibana Dashboard Fixture Generator
#
# This Dockerfile creates an environment that:
# 1. Bootstraps Kibana from source (to access @kbn/lens-embeddable-utils)
# 2. Provides LensConfigBuilder API for generating fixtures
# 3. Runs simple JavaScript scripts to export dashboard JSON
#
# Note: The first build takes 15-30 minutes due to Kibana bootstrap

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

# Clone Kibana (use build arg for version flexibility)
ARG KIBANA_VERSION=main
WORKDIR /kibana
RUN git clone --depth 1 --branch ${KIBANA_VERSION} https://github.com/elastic/kibana.git . || \
    git clone --depth 1 https://github.com/elastic/kibana.git .

# Bootstrap Kibana (this takes 15-30 minutes)
# This makes @kbn/lens-embeddable-utils and other packages available
RUN yarn kbn bootstrap

# Create tool workspace
WORKDIR /tool
RUN mkdir -p /tool/output /tool/examples

# Copy generator scripts
COPY package.json ./
COPY generate-all.js ./
COPY examples/ ./examples/

# Set output directory
ENV OUTPUT_DIR=/tool/output

# Set NODE_PATH so Node can find @kbn packages from Kibana
ENV NODE_PATH=/kibana/node_modules

# Default command: generate all fixtures
CMD ["node", "generate-all.js"]
