# Dashboard Lint Makefile
# Component-specific commands for the Python linting package

# Set SHELL before including Makefile.shared to ensure bash is used
ifdef RUNNER_OS
  ifeq ($(RUNNER_OS),Windows)
    SHELL := bash
  else
    SHELL := /bin/bash
  endif
else
  SHELL := /bin/bash
endif

# Include shared helpers
include ../../Makefile.shared

.PHONY: help all install ci check fix test test-coverage coverage-report lint lint-check typecheck clean build publish publish-test

help:
	@echo "Dashboard Lint Commands:"
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
	@echo "  lint              - Auto-fix Python linting issues (format + lint)"
	@echo "  lint-check        - Check Python linting without fixing"
	@echo ""
	@echo "Type Checking:"
	@echo "  typecheck     - Run Python type checking (basedpyright)"
	@echo ""
	@echo "Testing:"
	@echo "  test              - Run Python unit tests"
	@echo "  test-coverage     - Run tests with coverage"
	@echo "  coverage-report   - Open HTML coverage report"
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

ci: lint-check typecheck test
	$(call print_end, "Lint CI checks passed")

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
	$(call run_cmd, "Running type checking", cd ../.. && uv run --group dev basedpyright packages/kb-dashboard-lint, "Type checking passed")

# Testing
test:
	$(call run_cmd, "Running pytest", uv run pytest -o addopts="" --tb=line --no-header -q, "Tests passed")

test-coverage:
	$(call run_cmd, "Running pytest with coverage", uv run pytest --cov=src/dashboard_lint --cov-report=term-missing --cov-report=html --cov-report=json, "Coverage report generated")
	@echo "  HTML report: htmlcov/index.html"
	@echo "  JSON report: coverage.json"
	@echo ""
	@echo "Run 'make coverage-report' to open the HTML report in your browser"

coverage-report:
	$(call require_file, htmlcov/index.html, "Run 'make test-coverage' first")
	$(call run_cmd, "Opening coverage report", python -m webbrowser htmlcov/index.html || xdg-open htmlcov/index.html || open htmlcov/index.html, "Coverage report opened")

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
	$(call run_cmd, "Building package", uv build, "Package built successfully")

publish: build
	$(call run_cmd, "Publishing to PyPI", uv publish, "Package published to PyPI")

publish-test: build
	$(call run_cmd, "Publishing to TestPyPI", uv publish --publish-url https://test.pypi.org/legacy/, "Package published to TestPyPI")
