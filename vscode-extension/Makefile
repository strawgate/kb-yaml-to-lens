# VSCode Extension Makefile
# Component-specific commands for the kb-dashboard-compiler extension

.PHONY: help all install ci check fix test test-unit compile watch lint lint-check package clean

help:
	@echo "VSCode Extension Commands:"
	@echo "  all           - Default target (alias for ci)"
	@echo "  install       - Install npm dependencies"
	@echo "  ci            - Run all CI checks (compile + lint + test)"
	@echo "  check         - Alias for ci"
	@echo "  fix           - Auto-fix linting issues"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  compile       - Compile TypeScript"
	@echo "  watch         - Watch mode for development"
	@echo "  lint          - Check linting"
	@echo "  lint-check    - Alias for lint"
	@echo "  package       - Create .vsix package"
	@echo "  clean         - Clean build artifacts"

install:
	@echo "Installing VSCode extension dependencies..."
	npm ci

all: ci

ci: compile lint test-unit
	@echo "✓ VSCode extension CI checks passed"

check: ci

fix:
	@echo "Auto-fixing ESLint issues..."
	npm run lint -- --fix

test:
	@echo "Running VSCode extension tests..."
	npm test

test-unit:
	@echo "Running TypeScript tests for VSCode extension..."
	npm run compile && npm run test:unit

compile:
	@echo "Compiling TypeScript..."
	npm run compile

watch:
	@echo "Starting watch mode..."
	npm run watch

lint:
	@echo "Running ESLint..."
	npm run compile && npm run lint

lint-check: lint

package:
	@echo "Creating .vsix package..."
	npm run package

clean:
	@echo "Cleaning build artifacts..."
	rm -rf out/
	rm -rf node_modules/
