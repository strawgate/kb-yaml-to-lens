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

# Install git (required for git-based dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends git=1:2.47.3-0+deb13u1 && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Copy project files
# Note: Build context should be repository root for workspace uv.lock access
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
# Copy workspace dependencies (required for uv to resolve workspace deps)
COPY packages/kb-dashboard-cli/pyproject.toml packages/kb-dashboard-cli/README.md /app/packages/kb-dashboard-cli/
COPY packages/kb-dashboard-cli/src/ /app/packages/kb-dashboard-cli/src/
COPY packages/kb-dashboard-core/pyproject.toml packages/kb-dashboard-core/README.md /app/packages/kb-dashboard-core/
COPY packages/kb-dashboard-core/src/ /app/packages/kb-dashboard-core/src/
COPY packages/kb-dashboard-lint/pyproject.toml packages/kb-dashboard-lint/README.md /app/packages/kb-dashboard-lint/
COPY packages/kb-dashboard-lint/src/ /app/packages/kb-dashboard-lint/src/
COPY packages/kb-dashboard-tools/pyproject.toml packages/kb-dashboard-tools/README.md /app/packages/kb-dashboard-tools/
COPY packages/kb-dashboard-tools/src/ /app/packages/kb-dashboard-tools/src/

# Sync dependencies using uv (uses lockfile for reproducible builds)
RUN uv sync --frozen --no-dev && \
    mkdir -p /inputs /output && \
    addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --gid 1001 --home /home/appuser appuser && \
    mkdir -p /home/appuser/.cache/uv && \
    chown -R appuser:appuser /inputs /output /app /home/appuser

# Switch to non-root user
USER appuser

# Set environment variables for default paths
ENV INPUT_DIR=/inputs
ENV OUTPUT_DIR=/output

# Use uv run kb-dashboard as entrypoint for reproducible execution
ENTRYPOINT ["uv", "run", "kb-dashboard"]

# Default command: show help
CMD ["--help"]
