# Kibana Dashboard Fixture Generator
#
# This Dockerfile creates an environment that:
# 1. Bootstraps Kibana from source (to access @kbn/* packages)
# 2. Builds TypeScript dashboard definitions
# 3. Generates JSON fixtures using Kibana's APIs
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
# This makes @kbn/* packages available for import
RUN yarn kbn bootstrap

# Create tool directories
WORKDIR /tool
RUN mkdir -p /tool/output

# Copy tool source files
COPY package.json tsconfig.json ./
COPY src/ ./src/

# Install tool dependencies
RUN yarn install

# Build TypeScript
RUN yarn build

# Set output directory
ENV OUTPUT_DIR=/tool/output

# Default command: generate all fixtures
CMD ["node", "dist/cli.js"]
