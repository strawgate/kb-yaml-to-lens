

.PHONY: help install update-deps check check-fix test test-coverage test-links test-smoke clean clean-full lint lint-check format format-check lint-markdown lint-markdown-check inspector compile-docs docs-serve docs-build docs-deploy test-extension test-extension-python test-extension-typescript typecheck compile upload setup

help:
	@echo "Dependency Management:"
	@echo "  setup         - Set up the environment"
	@echo "  install       - Install dependencies using uv"
	@echo "  update-deps   - Update dependencies"
	@echo ""
	@echo "Build and Check:"
	@echo "  check         - Validate code without making changes (lint, typecheck, tests)"
	@echo "  check-fix     - Validate and auto-fix issues where possible"
	@echo ""
	@echo "Testing:"
	@echo "  test                     - Run unit tests"
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
	@echo "Cleaning:"
	@echo "  clean         - Clean up cache and temporary files"
	@echo "  clean-full    - Clean up all including virtual environment"
	@echo ""
	@echo "Linting and Formatting:"
	@echo "  lint              - Auto-fix linting and formatting issues"
	@echo "  lint-check        - Check for linting issues without fixing"
	@echo "  format            - Auto-format code with ruff"
	@echo "  format-check      - Check code formatting without fixing"
	@echo "  lint-markdown     - Auto-fix markdown linting issues"
	@echo "  lint-markdown-check - Check markdown without fixing"
	@echo "  typecheck         - Run type checking with basedpyright"
	@echo ""
	@echo "Documentation:"
	@echo "  compile-docs  - Regenerate YAML reference from source"
	@echo "  docs-serve    - Start local documentation server"
	@echo "  docs-build    - Build documentation static site"
	@echo "  docs-deploy   - Deploy documentation to GitHub Pages"
	@echo ""
	@echo "Helpers:"
	@echo "  inspector     - Run MCP Inspector"

install:
	@echo "Running uv sync..."
	uv sync --group dev
	@echo "Installing markdownlint-cli..."
	npm install -g markdownlint-cli

# Validation without auto-fixing (suitable for CI and pre-commit checks)
check: lint-check format-check lint-markdown-check typecheck test test-links test-smoke test-extension-python test-extension-typescript

# Validation with auto-fixing
check-fix: lint format lint-markdown typecheck test test-links test-smoke test-extension-python test-extension-typescript

test:
	@echo "Running pytest..."
	uv run pytest

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
	uv run python -m pytest vscode-extension/python/test_*.py -v

test-extension-typescript:
	@echo "Running TypeScript tests for VSCode extension..."
	# Using npm install for local development flexibility (vs npm ci in CI)
	cd vscode-extension && npm install && npm run compile && npm run test:unit


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
	uv run ruff check .

# Auto-format code
format:
	@echo "Running ruff format..."
	uv run ruff format .

# Check formatting without fixing
format-check:
	@echo "Running ruff format --check..."
	uv run ruff format . --check

# Auto-fix markdown issues
lint-markdown:
	@echo "Running markdownlint --fix..."
	markdownlint --fix -c .markdownlint.jsonc .

# Check markdown without fixing
lint-markdown-check:
	@echo "Running markdownlint..."
	markdownlint -c .markdownlint.jsonc .

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

compile-docs:
	@echo "Compiling documentation reference..."
	uv run python scripts/compile_docs.py

docs-serve:
	@echo "Starting documentation server..."
	uv run --extra docs mkdocs serve

docs-build:
	@echo "Building documentation..."
	uv run --extra docs mkdocs build

docs-deploy:
	@echo "Deploying documentation to GitHub Pages..."
	uv run --extra docs mkdocs gh-deploy --force