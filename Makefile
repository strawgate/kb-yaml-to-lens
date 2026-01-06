
.PHONY: all help install update-deps ci check fix lint-all lint-all-check test-all test test-coverage coverage-report test-links test-smoke clean clean-full lint lint-check format format-check lint-markdown lint-markdown-check lint-yaml lint-yaml-check lint-extension lint-extension-check build-extension install-extension inspector docs-serve docs-build docs-deploy test-extension test-extension-typescript typecheck compile upload setup test-extension-e2e docker-build docker-run docker-test docker-publish build-binary test-docker-smoke test-binary-smoke gh-get-review-threads gh-resolve-review-thread gh-get-latest-review gh-check-latest-review gh-get-comments-since gh-minimize-outdated-comments gh-check-repo-activity

# Docker configuration
DOCKER_IMAGE_NAME := kb-dashboard-compiler
DOCKER_IMAGE_TAG ?= latest
DOCKER_IMAGE := $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)
GHCR_REGISTRY := ghcr.io/strawgate/kb-yaml-to-lens/kb-dashboard-compiler:$(DOCKER_IMAGE_TAG)

# YAML linting exclusions
YAMLFIX_EXCLUDE := --exclude ".venv/**/*.yaml" --exclude ".venv/**/*.yml" --exclude "node_modules/**/*.yaml" --exclude "node_modules/**/*.yml"

all: ci

help:
	@echo "Dependency Management:"
	@echo "  setup         - Set up the environment"
	@echo "  install       - Install dependencies using uv"
	@echo "  update-deps   - Update dependencies"
	@echo ""
	@echo "CI and Development Workflow:"
	@echo "  all           - Run all CI checks (default target)"
	@echo "  ci            - Run all CI checks (compact output on success)"
	@echo "  check         - Same as 'ci' - validate everything before committing"
	@echo "  fix           - Auto-fix all linting issues (compact output)"
	@echo ""
	@echo "Linting (individual commands):"
	@echo "  lint-all          - Auto-fix ALL linting issues (Python, Markdown, YAML, Extension)"
	@echo "  lint-all-check    - Check ALL linting (Python, Markdown, YAML, Extension) without fixing"
	@echo "  lint              - Auto-fix Python linting issues (ruff check --fix)"
	@echo "  lint-check        - Check Python linting without fixing"
	@echo "  format            - Auto-format Python code (ruff format)"
	@echo "  format-check      - Check Python formatting without fixing"
	@echo "  lint-markdown     - Auto-fix markdown linting issues"
	@echo "  lint-markdown-check - Check markdown without fixing"
	@echo "  lint-yaml         - Auto-fix YAML linting issues"
	@echo "  lint-yaml-check   - Check YAML without fixing"
	@echo "  lint-extension    - Auto-fix TypeScript/Extension linting issues"
	@echo "  lint-extension-check - Check TypeScript/Extension linting without fixing"
	@echo ""
	@echo "Type Checking:"
	@echo "  typecheck     - Run Python type checking (basedpyright)"
	@echo ""
	@echo "Testing:"
	@echo "  test-all                 - Run ALL tests (unit, smoke, extension)"
	@echo "  test                     - Run Python unit tests"
	@echo "  test-coverage            - Run tests with coverage (HTML + terminal + JSON)"
	@echo "  coverage-report          - Open HTML coverage report in browser"
	@echo "  test-links               - Check documentation links"
	@echo "  test-smoke               - Run smoke tests"
	@echo "  test-extension           - Run all VSCode extension tests"
	@echo "  test-extension-typescript - Run TypeScript tests for extension"
	@echo "  test-extension-e2e       - Run E2E tests for extension (headless)"
	@echo ""
	@echo "VS Code Extension:"
	@echo "  install-extension    - Install extension dependencies"
	@echo "  build-extension      - Build extension for publishing"
	@echo ""
	@echo "Dashboard Compilation:"
	@echo "  compile       - Compile YAML dashboards to NDJSON (requires input-dir)"
	@echo "  upload        - Compile and upload dashboards to Kibana (requires input-dir)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs-serve    - Start local documentation server"
	@echo "  docs-build    - Build documentation static site"
	@echo "  docs-deploy   - Deploy documentation to GitHub Pages"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build       - Build Docker image for the compiler"
	@echo "  docker-run         - Run Docker container with sample inputs"
	@echo "  docker-test        - Test Docker image with basic help command"
	@echo "  docker-publish     - Publish multi-arch Docker image to GHCR"
	@echo "  test-docker-smoke  - Run comprehensive smoke tests on Docker image"
	@echo ""
	@echo "Binary Distribution:"
	@echo "  build-binary       - Build standalone binary for current platform"
	@echo "  test-binary-smoke  - Run comprehensive smoke tests on binary"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean         - Clean up cache and temporary files"
	@echo "  clean-full    - Clean up all including virtual environment"
	@echo ""
	@echo "GitHub Workflow Helpers:"
	@echo "  gh-get-review-threads        - Get PR review threads (OWNER REPO PR [AUTHOR])"
	@echo "  gh-resolve-review-thread     - Resolve review thread (OWNER REPO PR THREAD_ID [COMMENT])"
	@echo "  gh-get-latest-review         - Get latest review from author (OWNER REPO PR AUTHOR)"
	@echo "  gh-check-latest-review       - Check if review is latest (OWNER REPO PR AUTHOR REVIEW_ID)"
	@echo "  gh-get-comments-since        - Get comments since timestamp (OWNER REPO ISSUE SINCE [AUTHOR])"
	@echo "  gh-minimize-outdated-comments - Minimize outdated PR comments (OWNER REPO PR)"
	@echo "  gh-check-repo-activity       - Check repo activity (OWNER REPO SINCE [THRESHOLD])"
	@echo ""
	@echo "Helpers:"
	@echo "  inspector     - Run MCP Inspector"

install: install-extension
	@echo "Running uv sync..."
	uv sync --group dev
	@echo "Installing markdownlint-cli..."
	npm install -g markdownlint-cli

# CI and development workflow commands
ci: lint-all-check typecheck test-all docs-build-quiet
	@echo "✓ All CI checks passed!"

check: ci

fix: lint-all

# Linting meta-commands
lint-all: lint format lint-markdown lint-yaml lint-extension
	@echo "✓ All linting complete (with auto-fix)"

lint-all-check: lint-check format-check lint-markdown-check lint-yaml-check lint-extension-check
	@echo "✓ All linting checks passed"

# Testing meta-command
test-all: test test-smoke test-links test-extension-typescript
	@echo "✓ All tests passed"

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
	@uv run pytest --check-links docs/ README.md CONTRIBUTING.md -o addopts="" --tb=line --no-header -q

test-extension:
	@echo "Running VSCode extension tests..."
	cd vscode-extension && npm install && npm test

test-extension-typescript:
	@echo "Running TypeScript tests for VSCode extension..."
	# Using npm install for local development flexibility (vs npm ci in CI)
	@cd vscode-extension && npm install > /dev/null 2>&1 && npm run compile > /dev/null 2>&1 && npm run test:unit

test-extension-e2e:
	@echo "Running Extension E2E Tests..."
	@uv sync --group dev --extra lsp
	@. .venv/bin/activate && cd vscode-extension && npm install && xvfb-run -a npm test

# VS Code Extension build and dependency management
install-extension:
	@echo "Installing VSCode extension dependencies..."
	@cd vscode-extension && npm ci

build-extension:
	@echo "Building VSCode extension..."
	@cd vscode-extension && npm run vscode:prepublish

# Extension linting
lint-extension:
	@echo "Running ESLint on VSCode extension (auto-fix)..."
	@cd vscode-extension && npm run lint -- --fix 2>/dev/null || npm run lint

lint-extension-check:
	@echo "Running ESLint on VSCode extension..."
	@cd vscode-extension && npm run compile > /dev/null && npm run lint

inspector:
	@echo "Running MCP Inspector..."
	npx @modelcontextprotocol/inspector

test-smoke:
	uv run kb-dashboard --help

# Auto-fix linting issues
lint:
	@echo "Running ruff check --fix..."
	uv run ruff check . --fix

# Check for linting issues without fixing
lint-check:
	@echo "Running ruff check..."
	@uv run ruff check . --quiet

# Auto-format code
format:
	@echo "Running ruff format..."
	uv run ruff format .

# Check formatting without fixing
format-check:
	@echo "Running ruff format --check..."
	@uv run ruff format . --check --quiet

# Auto-fix markdown issues
lint-markdown:
	@echo "Running markdownlint --fix..."
	markdownlint --fix -c .markdownlint.jsonc .

# Check markdown without fixing
lint-markdown-check:
	@echo "Running markdownlint..."
	@markdownlint -c .markdownlint.jsonc . > /dev/null 2>&1 && echo "✓ Markdown checks passed" || (markdownlint -c .markdownlint.jsonc . && exit 1)

# Auto-fix YAML issues
lint-yaml:
	@echo "Running yamlfix..."
	uv run yamlfix $(YAMLFIX_EXCLUDE) .

# Check YAML without fixing
lint-yaml-check:
	@echo "Running yamlfix --check..."
	@uv run yamlfix --check $(YAMLFIX_EXCLUDE) . > /dev/null 2>&1 && echo "✓ YAML checks passed" || (uv run yamlfix --check $(YAMLFIX_EXCLUDE) . && exit 1)

typecheck:
	@echo "Running type checking..."
	uv run basedpyright

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ **/__pycache__
	rm -rf .pytest_cache **/.pytest_cache
	rm -rf .ruff_cache **/.ruff_cache
	rm -rf **/.pyc
	rm -rf **/.pyo

clean-full: clean
	@echo "Cleaning up all..."
	rm -rf .venv

setup:
	@echo "Setting up environment..."
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv sync --group dev
	echo "Environment set up successfully!"

update-deps:
	@echo "Updating dependencies..."
	uv lock --upgrade

compile:
	@echo "Compiling dashboards..."
	uv run kb-dashboard compile

upload:
	@echo "Compiling and uploading dashboards to Kibana..."
	uv run kb-dashboard compile --upload

docs-serve:
	@echo "Starting documentation server..."
	uv run --group docs mkdocs serve

docs-build:
	@echo "Building documentation..."
	uv run --group docs mkdocs build

docs-build-quiet:
	@echo "Building documentation (errors only)..."
	@uv run --group docs mkdocs build --quiet --strict && echo "✓ Documentation builds successfully"

docs-deploy:
	@echo "Deploying documentation to GitHub Pages..."
	uv run --group docs mkdocs gh-deploy --force

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE) .

docker-run:
	@echo "Running Docker container..."
	@mkdir -p $(PWD)/inputs $(PWD)/output
	@echo "Note: Mount your inputs directory with -v /path/to/inputs:/inputs"
	docker run --rm -v $(PWD)/inputs:/inputs -v $(PWD)/output:/output \
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
	@docker buildx version > /dev/null 2>&1 || (echo "Error: docker buildx not available. Install with: docker buildx install" && exit 1)
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t $(GHCR_REGISTRY) \
		--push .

# Binary build command
build-binary:
	@echo "Building standalone binary..."
	@uv sync --group build
	@uv run python scripts/build_binaries.py

# Docker smoke tests
test-docker-smoke:
	@echo "Running Docker smoke tests..."
	@bash scripts/test_docker_smoke.sh

# Binary smoke tests
test-binary-smoke:
	@echo "Running binary smoke tests..."
	@bash scripts/test_binary_smoke.sh

# GitHub Workflow Helper Commands
# These wrap the scripts in .github/scripts/ for easier use

gh-get-review-threads:
	@.github/scripts/gh-get-review-threads.sh $(filter-out $@,$(MAKECMDGOALS))

gh-resolve-review-thread:
	@.github/scripts/gh-resolve-review-thread.sh $(filter-out $@,$(MAKECMDGOALS))

gh-get-latest-review:
	@.github/scripts/gh-get-latest-review.sh $(filter-out $@,$(MAKECMDGOALS))

gh-check-latest-review:
	@.github/scripts/gh-check-latest-review.sh $(filter-out $@,$(MAKECMDGOALS))

gh-get-comments-since:
	@.github/scripts/gh-get-comments-since.sh $(filter-out $@,$(MAKECMDGOALS))

gh-minimize-outdated-comments:
	@.github/scripts/gh-minimize-outdated-comments.sh $(filter-out $@,$(MAKECMDGOALS))

gh-check-repo-activity:
	@.github/scripts/gh-check-repo-activity.sh $(filter-out $@,$(MAKECMDGOALS))

%:
	@:
