

.PHONY: help install update-deps uv-sync activate build check test test-smoke clean clean-full lint autocorrect format lint-markdown inspector docs-serve docs-build docs-deploy test-extension test-extension-python test-extension-typescript

help:
	@echo "Dependency Management:"
	@echo "  setup         - Set up the environment"
	@echo "  install       - Install dependencies using uv"
	@echo "  update-deps   - Update dependencies"

	@echo "Build and Check:"
	@echo "  build         - Build the project"
	@echo "  check         - Run linting and tests"

	@echo "Testing:"
	@echo "  test                  - Run unit tests"
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
	@echo "  - lint-autocorrect  - Run ruff check --fix"
	@echo "  - lint-format       - Run ruff format"
	@echo "  - lint-markdown     - Run markdownlint"

	@echo "Documentation:"
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

check: lint test test-smoke test-extension-python test-extension-typescript

test:
	@echo "Running pytest..."
	uv run pytest

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
	uv run es_knowledge_base_mcp --help

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
	uv run --extra docs mkdocs serve

docs-build:
	@echo "Building documentation..."
	uv run --extra docs mkdocs build

docs-deploy:
	@echo "Deploying documentation to GitHub Pages..."
	uv run --extra docs mkdocs gh-deploy --force