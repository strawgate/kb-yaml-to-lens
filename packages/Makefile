# Packages Makefile - Build and test for all Python packages
# This orchestrates all kb-dashboard-* packages in the workspace

.PHONY: help all install ci check fix test test-coverage test-smoke lint lint-check typecheck clean clean-full build publish publish-test

# YAML linting exclusions (operates on parent directory)
YAMLFIX_EXCLUDE := \
	--exclude ".venv/**/*.yaml" --exclude ".venv/**/*.yml" \
	--exclude "**/node_modules/**/*.yaml" --exclude "**/node_modules/**/*.yml"

help:
	@echo "Packages Commands (kb-dashboard-* namespace packages):"
	@echo ""
	@echo "Dependency Management:"
	@echo "  install       - Install Python dependencies using uv"
	@echo ""
	@echo "CI and Development Workflow:"
	@echo "  all           - Default target (alias for ci)"
	@echo "  ci            - Run all CI checks (lint + typecheck + test)"
	@echo "  check         - Alias for ci"
	@echo "  fix           - Auto-fix linting issues"
	@echo ""
	@echo "Linting:"
	@echo "  lint          - Auto-fix Python and YAML linting issues"
	@echo "  lint-check    - Check Python and YAML linting without fixing"
	@echo ""
	@echo "Type Checking:"
	@echo "  typecheck     - Run Python type checking (basedpyright)"
	@echo ""
	@echo "Testing:"
	@echo "  test          - Run Python unit tests"
	@echo "  test-coverage - Run tests with coverage"
	@echo ""
	@echo "PyPI Publishing:"
	@echo "  build         - Build all packages for PyPI"
	@echo "  publish       - Publish all packages to PyPI"
	@echo "  publish-test  - Publish all packages to TestPyPI"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean         - Clean cache and temporary files"
	@echo "  clean-full    - Clean all including virtual environment"

all: ci

install:
	@echo "Installing Python dependencies..."
	cd .. && uv sync --group dev

ci: lint-check typecheck test
	@echo "✓ Packages CI checks passed"

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
	@cd .. && uv run ruff format packages/
	@echo "Running ruff check --fix..."
	@cd .. && uv run ruff check packages/ --fix

lint-python-check:
	@echo "Running ruff format --check..."
	@cd .. && uv run ruff format packages/ --check --quiet
	@echo "Running ruff check..."
	@cd .. && uv run ruff check packages/ --quiet

# YAML linting
lint-yaml:
	@echo "Running yamlfix..."
	cd .. && uv run yamlfix $(YAMLFIX_EXCLUDE) .

lint-yaml-check:
	@echo "Running yamlfix --check..."
	@cd .. && uv run yamlfix --check $(YAMLFIX_EXCLUDE) . > /dev/null 2>&1 && echo "✓ YAML checks passed" || (cd .. && uv run yamlfix --check $(YAMLFIX_EXCLUDE) .)

# Type checking
typecheck:
	@echo "Running type checking..."
	cd .. && uv run basedpyright packages/

# Testing
test:
	@echo "Running pytest..."
	@cd .. && uv run pytest packages/kb-dashboard-core/tests packages/kb-dashboard-cli/tests packages/kb-dashboard-lsp/tests packages/kb-dashboard-tools/tests -o addopts="" --tb=line --no-header -q

test-coverage:
	@echo "Running pytest with coverage..."
	@cd .. && uv run pytest packages/kb-dashboard-core/tests packages/kb-dashboard-cli/tests packages/kb-dashboard-lsp/tests packages/kb-dashboard-tools/tests --cov=packages --cov-report=term-missing --cov-report=html --cov-report=json

test-smoke:
	@bash scripts/test_cli_smoke.sh

# Cleaning
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

clean-full: clean
	@echo "Deep cleaning..."
	rm -rf ../.venv

# PyPI Publishing
build:
	@echo "Building all packages..."
	@for pkg in kb-dashboard-core kb-dashboard-cli kb-dashboard-lsp kb-dashboard-tools; do \
		echo "Building $$pkg..."; \
		cd $$pkg && uv build && cd ..; \
	done
	@echo "✓ All packages built successfully"

publish: build
	@echo "Publishing all packages to PyPI..."
	@for pkg in kb-dashboard-core kb-dashboard-tools kb-dashboard-cli kb-dashboard-lsp; do \
		echo "Publishing $$pkg..."; \
		cd $$pkg && uv publish && cd ..; \
	done
	@echo "✓ All packages published to PyPI"

publish-test: build
	@echo "Publishing all packages to TestPyPI..."
	@for pkg in kb-dashboard-core kb-dashboard-tools kb-dashboard-cli kb-dashboard-lsp; do \
		echo "Publishing $$pkg to TestPyPI..."; \
		cd $$pkg && uv publish --publish-url https://test.pypi.org/legacy/ && cd ..; \
	done
	@echo "✓ All packages published to TestPyPI"
