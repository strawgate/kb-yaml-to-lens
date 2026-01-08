# VSCode Extension Makefile
# Component-specific commands for the kb-dashboard-compiler extension

.PHONY: help all install ci check fix test test-unit compile watch lint lint-check package clean copy-lsp-binary clean-binaries

help:
	@echo "VSCode Extension Commands:"
	@echo "  all              - Default target (alias for ci)"
	@echo "  install          - Install npm dependencies"
	@echo "  ci               - Run all CI checks (compile + lint + test)"
	@echo "  check            - Alias for ci"
	@echo "  fix              - Auto-fix linting issues"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  compile          - Compile TypeScript"
	@echo "  watch            - Watch mode for development"
	@echo "  lint             - Check linting"
	@echo "  lint-check       - Alias for lint"
	@echo "  package          - Create .vsix package"
	@echo "  copy-lsp-binary  - Copy LSP binary from compiler (current platform)"
	@echo "  clean            - Clean build artifacts"
	@echo "  clean-binaries   - Clean copied LSP binaries"

install:
	@echo "Installing VSCode extension dependencies..."
	npm ci

all: ci

ci:
	@if [ ! -d "node_modules" ]; then \
		echo "⚠ Dependencies not installed, installing..."; \
		$(MAKE) install; \
	fi; \
	$(MAKE) compile lint test-unit; \
	echo "✓ VSCode extension CI checks passed"

check: ci

fix:
	@if [ ! -d "node_modules" ]; then \
		echo "⚠ Dependencies not installed, installing..."; \
		$(MAKE) install; \
	fi; \
	echo "Auto-fixing ESLint issues..."; \
	npm run lint -- --fix

test:
	@if [ ! -d "node_modules" ]; then \
		echo "⚠ Dependencies not installed, installing..."; \
		$(MAKE) install; \
	fi; \
	echo "Running VSCode extension tests..."; \
	npm test

test-unit:
	@if [ ! -d "node_modules" ]; then \
		echo "⚠ Dependencies not installed, installing..."; \
		$(MAKE) install; \
	fi; \
	echo "Running TypeScript tests for VSCode extension..."; \
	npm run compile && npm run test:unit

compile:
	@if [ ! -d "node_modules" ]; then \
		echo "⚠ Dependencies not installed, installing..."; \
		$(MAKE) install; \
	fi; \
	echo "Compiling TypeScript..."; \
	npm run compile

watch:
	@echo "Starting watch mode..."
	npm run watch

lint:
	@if [ ! -d "node_modules" ]; then \
		echo "⚠ Dependencies not installed, installing..."; \
		$(MAKE) install; \
	fi; \
	echo "Running ESLint..."; \
	npm run compile && npm run lint

lint-check: lint

package:
	@echo "Creating .vsix package..."
	npm run package

copy-lsp-binary:
	@echo "Copying LSP binary from compiler..."
	bash scripts/copy_lsp_binary.sh

clean:
	@echo "Cleaning build artifacts..."
	rm -rf out/
	rm -rf node_modules/

clean-binaries:
	@echo "Cleaning copied LSP binaries..."
	rm -rf bin/
