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
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Copy project files
COPY pyproject.toml uv.lock README.md /app/
COPY src/ /app/src/

# Sync dependencies using uv (uses lockfile for reproducible builds)
RUN uv sync --frozen --no-dev && \
    mkdir -p /inputs /output && \
    addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --gid 1001 appuser && \
    chown -R appuser:appuser /inputs /output /app

# Switch to non-root user
USER appuser

# Set environment variables for default paths
ENV INPUT_DIR=/inputs
ENV OUTPUT_DIR=/output

# Use uv run kb-dashboard as entrypoint for reproducible execution
ENTRYPOINT ["uv", "run", "kb-dashboard"]

# Default command: show help
CMD ["--help"]
