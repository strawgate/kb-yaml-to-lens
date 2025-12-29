# Kibana Dashboard Fixture Generator
#
# This Dockerfile creates an environment that:
# 1. Bootstraps Kibana from source (to access @kbn/lens-embeddable-utils)
# 2. Provides LensConfigBuilder API for generating fixtures
# 3. Runs simple JavaScript scripts to export dashboard JSON
#
# Note: The first build takes ~6 minutes due to Kibana bootstrap and build

FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    build-essential \
    ca-certificates \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Clone Kibana FIRST to get the .node-version file
# Note: Kibana tags use "v" prefix (e.g., v9.2.0)
ARG KIBANA_VERSION=v9.2.0
WORKDIR /kibana
RUN git clone --depth 1 --branch ${KIBANA_VERSION} https://github.com/elastic/kibana.git . || \
    git clone --depth 1 --branch v${KIBANA_VERSION} https://github.com/elastic/kibana.git . || \
    git clone --depth 1 https://github.com/elastic/kibana.git .

# Install Node.js version specified by Kibana's .node-version file
ARG TARGETARCH
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN NODE_VERSION=$(cat .node-version) && \
    ARCH=$([ "$TARGETARCH" = "arm64" ] && echo "arm64" || echo "x64") && \
    echo "Installing Node.js ${NODE_VERSION} for ${ARCH}..." && \
    curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${ARCH}.tar.xz" | \
    tar -xJ -C /usr/local --strip-components=1 && \
    node --version

# Install Yarn Classic
RUN npm install -g yarn@1.22.19

# Set heap size for large builds
ENV NODE_OPTIONS="--max-old-space-size=8192"

# Bootstrap Kibana (this takes ~6 minutes)
# This makes @kbn/lens-embeddable-utils and other packages available
# Note: bootstrap also builds packages, including compiling .peggy grammar files
RUN yarn kbn bootstrap --allow-root

# Install tsx and peggy globally
# tsx: needed for TypeScript transpilation
# peggy: needed to compile .peggy grammar files to JavaScript
RUN npm install -g tsx@4.21.0 peggy

# Compile .peggy grammar files to JavaScript
# The kbn-es-query package has a grammar.peggy file that needs compilation
RUN cd /kibana/src/platform/packages/shared/kbn-es-query/src/kuery/grammar && \
    peggy grammar.peggy && \
    sed -i "s|from './grammar.peggy'|from './grammar.js'|g" index.ts

# Copy generator scripts to Kibana root (for proper @kbn/ module resolution)
COPY generate-all.js /kibana/
COPY dataviews-mock.js /kibana/
COPY examples/ /kibana/examples/
RUN mkdir -p /kibana/output

# Stay in Kibana root for module resolution
WORKDIR /kibana

# Set output directory and Kibana version for fixture generation
ENV OUTPUT_DIR=/kibana/output
ENV KIBANA_VERSION=${KIBANA_VERSION}

# Default command: generate all fixtures using tsx for TypeScript support
CMD ["tsx", "generate-all.js"]
