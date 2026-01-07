# Kibana Dashboard Compiler
#
# This Dockerfile creates a lightweight container for the kb-dashboard compiler tool.
# It allows you to compile YAML dashboards to Kibana NDJSON format in a containerized environment.
#
# Build:
#   docker build -t kb-dashboard-compiler:latest .
#
# Usage examples:
#   # Compile dashboards from local directory
#   docker run --rm -v $(pwd)/inputs:/inputs -v $(pwd)/output:/output \
#     kb-dashboard-compiler:latest compile --input-dir /inputs --output-dir /output
#
#   # Upload to Kibana
#   docker run --rm -v $(pwd)/inputs:/inputs \
#     kb-dashboard-compiler:latest compile --input-dir /inputs --upload \
#     --kibana-url http://host.docker.internal:5601 \
#     --kibana-username elastic --kibana-password changeme

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv==0.9.18

# Copy project files
COPY pyproject.toml /app/
COPY README.md /app/
COPY src/ /app/src/

# Install dependencies using uv and create directories
RUN uv pip install --system --no-cache . && \
    mkdir -p /inputs /output && \
    addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --gid 1001 appuser && \
    chown -R appuser:appuser /inputs /output /app

# Switch to non-root user
USER appuser

# Set environment variables for default paths
ENV INPUT_DIR=/inputs
ENV OUTPUT_DIR=/output

# Use kb-dashboard as entrypoint
ENTRYPOINT ["kb-dashboard"]

# Default command: show help
CMD ["--help"]
