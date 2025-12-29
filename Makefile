

.PHONY: help install update-deps check test test-coverage test-links test-smoke clean clean-full lint autocorrect format lint-markdown inspector compile-docs docs-serve docs-build docs-deploy test-extension test-extension-python test-extension-typescript typecheck compile upload setup

help:
	@echo "Dependency Management:"
	@echo "  setup         - Set up the environment"
	@echo "  install       - Install dependencies using uv"
	@echo "  update-deps   - Update dependencies"

	@echo "Build and Check:"
	@echo "  check         - Run linting, type checking, and tests"

	@echo "Testing:"
	@echo "  test                  - Run unit tests"
	@echo "  test-coverage         - Run tests with coverage report"
	@echo "  test-links            - Check documentation links"
	@echo "  test-smoke            - Run smoke tests"
	@echo "  test-extension        - Run all VSCode extension tests"
	@echo "  test-extension-python - Run Python tests for extension"
	@echo "  test-extension-typescript - Run TypeScript tests for extension"

	@echo "Dashboard Compilation:"
	@echo "  compile       - Compile YAML dashboards to NDJSON"
	@echo "  upload        - Compile and upload dashboards to Kibana"

	@echo "Cleaning:"
	@echo "  clean-full    - Clean up all including virtual environment"
	@echo "  - clean       - Clean up cache and temporary files"

	@echo "Linting:"
	@echo "  lint                - Run format, autocorrect, and markdown linting"
	@echo "  typecheck           - Run type checking with basedpyright"
	@echo "  - lint-autocorrect  - Run ruff check --fix"
	@echo "  - lint-format       - Run ruff format"
	@echo "  - lint-markdown     - Run markdownlint"

	@echo "Documentation:"
	@echo "  compile-docs  - Regenerate YAML reference from source"
	@echo "  docs-serve    - Start local documentation server"
	@echo "  docs-build    - Build documentation static site"
	@echo "  docs-deploy   - Deploy documentation to GitHub Pages"

	@echo "Helpers:"
	@echo "  inspector     - Run MCP Inspector"

install:
	@echo "Running uv sync..."
	uv sync --group dev
	@echo "Installing markdownlint-cli..."
	npm install -g markdownlint-cli

check: lint typecheck test test-links test-smoke test-extension-python test-extension-typescript

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

lint: autocorrect format lint-markdown

autocorrect:
	@echo "Running ruff check --fix..."
	uv run ruff check . --fix

format:
	@echo "Running ruff format..."
	uv run ruff format .

lint-markdown:
	@echo "Running markdownlint..."
	markdownlint --fix -c .markdownlint.jsonc .

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