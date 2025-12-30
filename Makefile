

.PHONY: help install update-deps ci check fix lint-all lint-all-check test-all test test-coverage test-links test-smoke clean clean-full lint lint-check format format-check lint-markdown lint-markdown-check lint-yaml lint-yaml-check inspector docs-serve docs-build docs-deploy test-extension test-extension-python test-extension-typescript typecheck compile upload setup

help:
	@echo "Dependency Management:"
	@echo "  setup         - Set up the environment"
	@echo "  install       - Install dependencies using uv"
	@echo "  update-deps   - Update dependencies"
	@echo ""
	@echo "CI and Development Workflow:"
	@echo "  ci            - Run all CI checks (compact output on success)"
	@echo "  check         - Same as 'ci' - validate everything before committing"
	@echo "  fix           - Auto-fix all linting issues (compact output)"
	@echo ""
	@echo "Linting (individual commands):"
	@echo "  lint-all          - Auto-fix ALL linting issues (Python, Markdown, YAML)"
	@echo "  lint-all-check    - Check ALL linting (Python, Markdown, YAML) without fixing"
	@echo "  lint              - Auto-fix Python linting issues (ruff check --fix)"
	@echo "  lint-check        - Check Python linting without fixing"
	@echo "  format            - Auto-format Python code (ruff format)"
	@echo "  format-check      - Check Python formatting without fixing"
	@echo "  lint-markdown     - Auto-fix markdown linting issues"
	@echo "  lint-markdown-check - Check markdown without fixing"
	@echo "  lint-yaml         - Auto-fix YAML linting issues"
	@echo "  lint-yaml-check   - Check YAML without fixing"
	@echo ""
	@echo "Type Checking:"
	@echo "  typecheck     - Run Python type checking (basedpyright)"
	@echo ""
	@echo "Testing:"
	@echo "  test-all                 - Run ALL tests (unit, smoke, extension)"
	@echo "  test                     - Run Python unit tests"
	@echo "  test-coverage            - Run tests with coverage report"
	@echo "  test-links               - Check documentation links"
	@echo "  test-smoke               - Run smoke tests"
	@echo "  test-extension           - Run all VSCode extension tests"
	@echo "  test-extension-python    - Run Python tests for extension"
	@echo "  test-extension-typescript - Run TypeScript tests for extension"
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
	@echo "Cleaning:"
	@echo "  clean         - Clean up cache and temporary files"
	@echo "  clean-full    - Clean up all including virtual environment"
	@echo ""
	@echo "Helpers:"
	@echo "  inspector     - Run MCP Inspector"

install:
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
lint-all: lint format lint-markdown lint-yaml
	@echo "✓ All linting complete (with auto-fix)"

lint-all-check: lint-check format-check lint-markdown-check lint-yaml-check
	@echo "✓ All linting checks passed"

# Testing meta-command
test-all: test test-smoke test-links test-extension-python test-extension-typescript
	@echo "✓ All tests passed"

test:
	@echo "Running pytest..."
	@uv run pytest -o addopts="" --tb=line --no-header -q

test-coverage:
	@echo "Running pytest with coverage..."
	uv run pytest --cov=src/dashboard_compiler --cov-report=term-missing --cov-report=html --cov-report=json

test-links:
	@echo "Checking documentation links..."
	uv run pytest --check-links docs/ README.md CONTRIBUTING.md

test-extension:
	@echo "Running VSCode extension tests..."
	cd vscode-extension && npm install && npm test

test-extension-python:
	@echo "Running Python tests for VSCode extension..."
	@uv run python -m pytest vscode-extension/python/test_*.py -o addopts="" --tb=line --no-header -q

test-extension-typescript:
	@echo "Running TypeScript tests for VSCode extension..."
	# Using npm install for local development flexibility (vs npm ci in CI)
	@cd vscode-extension && npm install > /dev/null 2>&1 && npm run compile > /dev/null 2>&1 && npm run test:unit


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
	uv run yamlfix .

# Check YAML without fixing
lint-yaml-check:
	@echo "Running yamllint..."
	@uv run yamllint . > /dev/null 2>&1 && echo "✓ YAML checks passed" || (uv run yamllint . && exit 1)

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