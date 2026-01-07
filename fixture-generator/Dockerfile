# Kibana Dashboard Fixture Generator
#
# This Dockerfile creates an environment that:
# 1. Uses pre-built Kibana base image (with @kbn/lens-embeddable-utils)
# 2. Provides LensConfigBuilder API for generating fixtures
# 3. Runs simple JavaScript scripts to export dashboard JSON
#
# Note: Uses pre-built base image from GHCR (~30 seconds)
#       To build locally from source, use Dockerfile.base (~6 minutes)

ARG KIBANA_VERSION=v9.2.0
ARG BASE_IMAGE=ghcr.io/strawgate/kb-yaml-to-lens/kibana-base:${KIBANA_VERSION}

FROM ${BASE_IMAGE}

# Copy generator scripts to Kibana root (for proper @kbn/ module resolution)
COPY generate-all.js /kibana/
COPY dataviews-mock.js /kibana/
COPY generator-utils.ts /kibana/
COPY examples/ /kibana/examples/
RUN mkdir -p /kibana/output

# Stay in Kibana root for module resolution
WORKDIR /kibana

# Set output directory and Kibana version for fixture generation
ENV OUTPUT_DIR=/kibana/output
ENV KIBANA_VERSION=${KIBANA_VERSION}

# Default command: generate all fixtures using tsx for TypeScript support
CMD ["tsx", "generate-all.js"]
