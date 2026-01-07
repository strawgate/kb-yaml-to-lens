# Dashboard Compiler Makefile
# Component-specific commands for the Python compiler

.PHONY: help all install ci check fix test test-coverage coverage-report test-links test-smoke lint lint-check typecheck compile upload docs-serve docs-build docs-build-quiet docs-deploy docker-build docker-run docker-test docker-publish test-docker-smoke build-binary test-binary-smoke setup update-deps clean clean-full lint-python lint-python-check lint-yaml lint-yaml-check

# Docker configuration
DOCKER_IMAGE_NAME := kb-dashboard-compiler
DOCKER_IMAGE_TAG ?= latest
DOCKER_IMAGE := $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)
GHCR_REGISTRY := ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:$(DOCKER_IMAGE_TAG)

# YAML linting exclusions (operates on parent directory)
YAMLFIX_EXCLUDE := \
	--exclude ".venv/**/*.yaml" --exclude ".venv/**/*.yml" \
	--exclude "compiler/.venv/**/*.yaml" --exclude "compiler/.venv/**/*.yml" \
	--exclude "node_modules/**/*.yaml" --exclude "node_modules/**/*.yml" \
	--exclude "vscode-extension/node_modules/**/*.yaml" --exclude "vscode-extension/node_modules/**/*.yml" \
	--exclude "fixture-generator/node_modules/**/*.yaml" --exclude "fixture-generator/node_modules/**/*.yml"

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
	@echo "  ci            - Run all CI checks (lint + typecheck + test + docs)"
	@echo "  check         - Alias for ci"
	@echo "  fix           - Auto-fix linting issues"
	@echo ""
	@echo "Linting:"
	@echo "  lint          - Auto-fix Python and YAML linting issues"
	@echo "  lint-check    - Check Python and YAML linting without fixing"
	@echo "  lint-python       - Auto-fix Python issues (format + lint)"
	@echo "  lint-python-check - Check Python without fixing"
	@echo "  lint-yaml         - Auto-fix YAML issues"
	@echo "  lint-yaml-check   - Check YAML without fixing"
	@echo ""
	@echo "Type Checking:"
	@echo "  typecheck     - Run Python type checking (basedpyright)"
	@echo ""
	@echo "Testing:"
	@echo "  test              - Run Python unit tests"
	@echo "  test-coverage     - Run tests with coverage"
	@echo "  coverage-report   - Open HTML coverage report"
	@echo "  test-links        - Check documentation links"
	@echo "  test-smoke        - Run smoke tests"
	@echo ""
	@echo "Dashboard Compilation:"
	@echo "  compile       - Compile YAML dashboards to NDJSON"
	@echo "  upload        - Compile and upload dashboards to Kibana"
	@echo ""
	@echo "Documentation:"
	@echo "  docs-serve    - Start local documentation server"
	@echo "  docs-build    - Build documentation static site"
	@echo "  docs-deploy   - Deploy documentation to GitHub Pages"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build       - Build Docker image"
	@echo "  docker-run         - Run Docker container"
	@echo "  docker-test        - Test Docker image"
	@echo "  docker-publish     - Publish Docker image to GHCR"
	@echo "  test-docker-smoke  - Run Docker smoke tests"
	@echo ""
	@echo "Binary Distribution:"
	@echo "  build-binary       - Build standalone binary"
	@echo "  test-binary-smoke  - Run binary smoke tests"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean         - Clean cache and temporary files"
	@echo "  clean-full    - Clean all including virtual environment"

all: ci

install:
	@echo "Installing Python dependencies..."
	uv sync --group dev

ci: lint-check typecheck test docs-build-quiet
	@echo "✓ Compiler CI checks passed"

check: ci

fix: lint

# Combined linting
lint: lint-python lint-yaml
	@echo "✓ All linting complete (with auto-fix)"

lint-check: lint-python-check lint-yaml-check
	@echo "✓ All linting checks passed"

# Python linting
lint-python:
	@echo "Running ruff format..."
	@uv run ruff format .
	@echo "Running ruff check --fix..."
	@uv run ruff check . --fix

lint-python-check:
	@echo "Running ruff format --check..."
	@uv run ruff format . --check --quiet
	@echo "Running ruff check..."
	@uv run ruff check . --quiet

# YAML linting (operates on parent directory)
lint-yaml:
	@echo "Running yamlfix..."
	uv run yamlfix $(YAMLFIX_EXCLUDE) ..

lint-yaml-check:
	@echo "Running yamlfix --check..."
	@uv run yamlfix --check $(YAMLFIX_EXCLUDE) .. > /dev/null 2>&1 && echo "✓ YAML checks passed" || uv run yamlfix --check $(YAMLFIX_EXCLUDE) ..

# Type checking
typecheck:
	@echo "Running type checking..."
	uv run basedpyright

# Testing
test:
	@echo "Running pytest..."
	@uv run pytest -o addopts="" --tb=line --no-header -q

test-coverage:
	@echo "Running pytest with coverage..."
	@uv run pytest --cov=src/dashboard_compiler --cov-report=term-missing --cov-report=html --cov-report=json
	@echo ""
	@echo "✓ Coverage report generated:"
	@echo "  • HTML report: htmlcov/index.html"
	@echo "  • JSON report: coverage.json"
	@echo ""
	@echo "Run 'make coverage-report' to open the HTML report in your browser"

coverage-report:
	@echo "Opening coverage report..."
	@if [ ! -f htmlcov/index.html ]; then \
		echo "Error: Coverage report not found. Run 'make test-coverage' first."; \
		exit 1; \
	fi
	@python -m webbrowser htmlcov/index.html || xdg-open htmlcov/index.html || open htmlcov/index.html

test-links:
	@echo "Checking documentation links..."
	@uv run pytest --check-links ../docs/ ../README.md ../CONTRIBUTING.md -o addopts="" --tb=line --no-header -q

test-smoke:
	uv run kb-dashboard --help

# Dependency management
setup:
	@echo "Setting up environment..."
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv sync --group dev
	@echo "✓ Environment set up successfully!"

update-deps:
	@echo "Updating dependencies..."
	uv lock --upgrade

# Compilation
compile:
	@echo "Compiling dashboards..."
	uv run kb-dashboard compile

upload:
	@echo "Compiling and uploading dashboards to Kibana..."
	uv run kb-dashboard compile --upload

# Documentation (references parent mkdocs.yml)
docs-serve:
	@echo "Starting documentation server..."
	uv run --group docs mkdocs serve -f ../mkdocs.yml

docs-build:
	@echo "Building documentation..."
	uv run --group docs mkdocs build -f ../mkdocs.yml

docs-build-quiet:
	@echo "Building documentation (errors only)..."
	@uv run --group docs mkdocs build --quiet --strict -f ../mkdocs.yml && echo "✓ Documentation builds successfully"

docs-deploy:
	@echo "Deploying documentation to GitHub Pages..."
	uv run --group docs mkdocs gh-deploy --force -f ../mkdocs.yml

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE) -f Dockerfile .

docker-run:
	@echo "Running Docker container..."
	@mkdir -p $(PWD)/inputs $(PWD)/../output
	@echo "Note: Mount your inputs directory with -v /path/to/inputs:/inputs"
	docker run --rm -v $(PWD)/inputs:/inputs -v $(PWD)/../output:/output \
		$(DOCKER_IMAGE) compile --input-dir /inputs --output-dir /output

docker-test:
	@echo "Testing Docker image..."
	docker run --rm $(DOCKER_IMAGE) --help

docker-publish:
	@echo "Publishing Docker image to GHCR..."
	@if [ "$(CONFIRM_PUBLISH)" != "yes" ]; then \
		echo "Error: Set CONFIRM_PUBLISH=yes to confirm publishing to GHCR"; \
		echo "Usage: make docker-publish CONFIRM_PUBLISH=yes"; \
		exit 1; \
	fi
	@docker buildx version > /dev/null 2>&1 || (echo "Error: docker buildx not available. See https://docs.docker.com/build/buildx/install/" && exit 1)
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t $(GHCR_REGISTRY) \
		-f Dockerfile \
		--push .

test-docker-smoke:
	@echo "Running Docker smoke tests..."
	@bash ../scripts/test_docker_smoke.sh

# Binary building
build-binary:
	@echo "Building standalone binary..."
	@uv sync --group build
	@uv run python ../scripts/build_binaries.py

test-binary-smoke:
	@echo "Running binary smoke tests..."
	@bash ../scripts/test_binary_smoke.sh

# Cleaning
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ **/__pycache__
	rm -rf .pytest_cache **/.pytest_cache
	rm -rf .ruff_cache **/.ruff_cache
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

clean-full: clean
	@echo "Cleaning up all..."
	rm -rf .venv
