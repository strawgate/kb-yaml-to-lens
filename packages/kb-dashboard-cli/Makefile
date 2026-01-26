# Dashboard Compiler Makefile
# Component-specific commands for the Python compiler

# Include shared helpers (SHELL is set automatically by Makefile.shared based on RUNNER_OS)
include ../../Makefile.shared

.PHONY: help all install ci check fix test test-unit test-e2e test-coverage coverage-report lint lint-check typecheck compile upload docker-build docker-run docker-test docker-publish setup update-deps clean build publish publish-test export-schemas

# Docker configuration
DOCKER_IMAGE_NAME := kb-dashboard-compiler
DOCKER_IMAGE_TAG ?= latest
DOCKER_IMAGE := $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)
GHCR_REGISTRY := ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:$(DOCKER_IMAGE_TAG)

help:
	@echo "Dashboard Compiler Commands:"
	@echo ""
	@echo "Dependency Management:"
	@echo "  install       - Install Python dependencies using uv"
	@echo "  setup         - Set up environment from scratch"
	@echo "  update-deps   - Update dependencies"
	@echo ""
	@echo "CI and Development Workflow:"
	@echo "  all           - Default target (alias for ci)"
	@echo "  ci            - Run all CI checks (lint + typecheck + test)"
	@echo "  check         - Alias for ci"
	@echo "  fix           - Auto-fix linting issues"
	@echo ""
	@echo "Linting:"
	@echo "  lint              - Auto-fix Python linting issues (format + lint)"
	@echo "  lint-check        - Check Python linting without fixing"
	@echo ""
	@echo "Type Checking:"
	@echo "  typecheck     - Run Python type checking (basedpyright)"
	@echo ""
	@echo "Testing:"
	@echo "  test              - Run all tests (unit + E2E)"
	@echo "  test-unit         - Run unit tests only"
	@echo "  test-e2e          - Run E2E tests (CLI compilation pipeline + Docker smoke tests)"
	@echo "  test-coverage     - Run tests with coverage"
	@echo "  coverage-report   - Open HTML coverage report"
	@echo ""
	@echo "Schema Export:"
	@echo "  export-schemas    - Export LSP response schemas as JSON"
	@echo ""
	@echo "Dashboard Compilation:"
	@echo "  compile       - Compile YAML dashboards to NDJSON"
	@echo "  upload        - Compile and upload dashboards to Kibana"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build       - Build Docker image"
	@echo "  docker-run         - Run Docker container"
	@echo "  docker-test        - Test Docker image"
	@echo "  docker-publish     - Publish Docker image to GHCR"
	@echo ""
	@echo "PyPI Publishing:"
	@echo "  build         - Build package for PyPI"
	@echo "  publish       - Publish package to PyPI"
	@echo "  publish-test  - Publish package to TestPyPI"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean         - Clean cache, temporary files, and virtual environment"
	@echo ""

all: ci

install:
	$(call run_cmd, "Installing Python dependencies", uv sync --group dev, "Python dependencies installed")

ci: lint-check typecheck test-unit test-e2e
	$(call print_end, "Compiler CI checks passed")

check: ci

fix: lint

# Python linting
lint:
	$(call run_cmd, "Running ruff format", uv run ruff format ., "ruff format complete")
	$(call run_cmd, "Running ruff check --fix", uv run ruff check . --fix, "ruff check complete")

lint-check:
	$(call run_cmd, "Running ruff format --check", uv run ruff format . --check --quiet, "ruff format check passed")
	$(call run_cmd, "Running ruff check", uv run ruff check . --quiet, "ruff check passed")
	$(call print_end, "Python linting checks passed")

# Type checking
typecheck:
	$(call print_start, "Running type checking")
	@cd $(ROOT) && output=$$(uv run --group dev basedpyright packages/kb-dashboard-cli --level error 2>&1); \
		echo "$$output" | sed 's/^/    /'; \
		if echo "$$output" | grep -q "0 errors"; then exit 0; else exit 1; fi
	$(call print_end, "Type checking passed")

# Testing
test-unit:
	$(call run_cmd, "Running pytest", uv run pytest -o addopts="" --tb=line --no-header -q, "Tests passed")

test-e2e:
	$(call run_cmd, "Running CLI E2E tests", bash scripts/test_cli_smoke.sh, "CLI E2E tests passed")
	$(call print_start, "Running Docker E2E tests")
	@if command -v docker > /dev/null 2>&1 && docker info > /dev/null 2>&1; then \
		$(MAKE) docker-build; \
		bash scripts/test_docker_smoke.sh $(INDENT); \
	else \
		echo "⚠ Docker not available, skipping Docker E2E tests"; \
	fi
	$(call print_end, "Docker E2E tests passed")

test: test-unit test-e2e

test-coverage:
	$(call run_cmd, "Running pytest with coverage", uv run pytest --cov=src/dashboard_compiler --cov-report=term-missing --cov-report=html --cov-report=json, "Coverage report generated")
	@echo "  • HTML report: htmlcov/index.html"
	@echo "  • JSON report: coverage.json"
	@echo ""
	@echo "Run 'make coverage-report' to open the HTML report in your browser"

coverage-report:
	$(call require_file, htmlcov/index.html, "Run 'make test-coverage' first")
	$(call run_cmd, "Opening coverage report", python -m webbrowser htmlcov/index.html || xdg-open htmlcov/index.html || open htmlcov/index.html, "Coverage report opened")

# Dependency management
setup:
	$(call run_cmd, "Installing uv", curl -LsSf https://astral.sh/uv/install.sh | sh, "uv installed")
	$(call run_cmd, "Installing Python dependencies", uv sync --group dev, "Dependencies installed")
	$(call print_end, "Environment set up successfully!")

update-deps:
	$(call run_cmd, "Updating dependencies", uv lock --upgrade, "Dependencies updated")

# Schema Export
export-schemas:
	$(call run_cmd, "Exporting LSP schemas", uv run python scripts/export_lsp_schemas.py, "Schemas exported")

# Compilation
compile:
	$(call run_cmd, "Compiling dashboards", uv run kb-dashboard compile, "Dashboards compiled")

upload:
	$(call run_cmd, "Compiling and uploading dashboards to Kibana", uv run kb-dashboard compile --upload, "Dashboards compiled and uploaded")

# Docker commands
docker-build:
	$(call run_cmd, "Building Docker image", cd $(ROOT) && docker build -t $(DOCKER_IMAGE) -f packages/kb-dashboard-cli/Dockerfile ., "Docker image built")

docker-run:
	@mkdir -p $(PWD)/inputs $(PWD)/../output
	@echo "Note: Mount your inputs directory with -v /path/to/inputs:/inputs"
	$(call run_cmd, "Running Docker container", docker run --rm -v $(PWD)/inputs:/inputs -v $(PWD)/../output:/output $(DOCKER_IMAGE) compile --input-dir /inputs --output-dir /output, "Docker container completed")

docker-test:
	$(call run_cmd, "Testing Docker image", docker run --rm $(DOCKER_IMAGE) --help, "Docker image test passed")

docker-publish: docker-build
	$(call require_var, CONFIRM_PUBLISH, "Set CONFIRM_PUBLISH=yes to confirm publishing to GHCR. Usage: make docker-publish CONFIRM_PUBLISH=yes")
	@docker buildx version > /dev/null 2>&1 || (echo "Error: docker buildx not available. See https://docs.docker.com/build/buildx/install/" && exit 1)
	$(call print_start, "Building and publishing multi-arch Docker image to GHCR")
	@if [ -n "$(DOCKER_TAGS)" ]; then \
		FIRST_TAG=$$(echo "$(DOCKER_TAGS)" | head -n1 | tr -d ' '); \
		cd $(ROOT) && docker buildx build --platform linux/amd64,linux/arm64 -t $$FIRST_TAG -f packages/kb-dashboard-cli/Dockerfile --push . $(INDENT); \
		for tag in $(DOCKER_TAGS); do \
			if [ "$$tag" != "$$FIRST_TAG" ]; then \
				printf "  Tagging and pushing %s\n" "$$tag"; \
				docker buildx imagetools create -t $$tag $$FIRST_TAG || exit 1; \
			fi; \
		done; \
	else \
		cd $(ROOT) && docker buildx build --platform linux/amd64,linux/arm64 -t $(GHCR_REGISTRY) -f packages/kb-dashboard-cli/Dockerfile --push . $(INDENT); \
	fi
	$(call print_end, "Docker image published to GHCR")

# Cleaning
clean:
	$(call print_start, "Cleaning up")
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
	@rm -rf .venv htmlcov/ .coverage coverage.json 2>/dev/null || true
	$(call print_end, "Cleanup complete")

# PyPI Publishing
build:
	$(call run_cmd, "Building package", uv build --out-dir $(ROOT)/dist, "Package built successfully")

publish: build
	$(call run_cmd, "Publishing to PyPI", uv publish $(ROOT)/dist/kb_dashboard_cli-*.tar.gz $(ROOT)/dist/kb_dashboard_cli-*.whl, "Package published to PyPI")

publish-test: build
	$(call run_cmd, "Publishing to TestPyPI", uv publish --publish-url https://test.pypi.org/legacy/ $(ROOT)/dist/kb_dashboard_cli-*.tar.gz $(ROOT)/dist/kb_dashboard_cli-*.whl, "Package published to TestPyPI")
