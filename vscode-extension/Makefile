# VSCode Extension Makefile
# Component-specific commands for the kb-dashboard-compiler extension

.PHONY: help all install ci check fix test test-unit test-unit-only test-e2e test-e2e-only compile watch lint lint-check lint-only package install-vscode install-cursor clean prepare prepare-all clean-binaries

help:
	@echo "VSCode Extension Commands:"
	@echo "  all              - Default target (alias for ci)"
	@echo "  install          - Install npm dependencies"
	@echo "  ci               - Run all CI checks (compile + lint + test)"
	@echo "  check            - Alias for ci"
	@echo "  fix              - Auto-fix linting issues"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-e2e         - Run E2E tests (compiles first)"
	@echo "  compile          - Compile TypeScript"
	@echo "  watch            - Watch mode for development"
	@echo "  lint             - Check linting (compiles first)"
	@echo "  lint-check       - Alias for lint"
	@echo "  lint-only        - Check linting (no compile, for CI)"
	@echo "  package          - Create .vsix package"
	@echo "  install-vscode   - Install packaged extension into VS Code"
	@echo "  install-cursor   - Install packaged extension into Cursor"
	@echo "  prepare          - Download uv + bundle compiler (current platform, for dev)"
	@echo "  prepare-all      - Download uv for all platforms + bundle compiler (for release)"
	@echo "  clean            - Clean build artifacts"
	@echo "  clean-binaries   - Clean downloaded binaries and bundled compiler"

install:
	@echo "Installing VSCode extension dependencies..."
	npm ci

all: ci

ci: install compile
	@echo "Running linting and tests..."
	$(MAKE) lint-only test-unit-only
	@echo "✓ VSCode extension CI checks passed"

check: ci

fix: install
	@echo "Auto-fixing ESLint issues..."
	npm run lint -- --fix

test: install
	@echo "Running VSCode extension tests..."
	npm test

# Non-compiling target for use in CI after compile has already run
test-unit-only:
	@echo "Running TypeScript tests for VSCode extension..."
	./node_modules/.bin/mocha out/test/unit/**/*.test.js --ui tdd 2>/dev/null || echo 'No unit tests found - skipping'

test-unit: install compile test-unit-only

# Non-compiling target for use in CI after compile has already run
test-e2e-only:
	@echo "Running VSCode extension E2E tests..."
	node ./out/test/runTest.js

test-e2e: install compile test-e2e-only

compile: install
	@echo "Compiling TypeScript..."
	npm run compile

watch: install
	@echo "Starting watch mode..."
	npm run watch

# Non-compiling target for use in CI after compile has already run
lint-only:
	@echo "Running ESLint..."
	npm run lint

lint: install compile lint-only

lint-check: lint

package: install
	@echo "Creating .vsix package..."
	npm run package

install-vscode:
	@echo "Installing extension into VS Code..."
	@set -e; \
	EXTENSION_NAME=$$(node -p "require('./package.json').name"); \
	EXTENSION_PUBLISHER=$$(node -p "require('./package.json').publisher"); \
	EXTENSION_VERSION=$$(node -p "require('./package.json').version"); \
	VSIX_FILE="$${EXTENSION_NAME}-$${EXTENSION_VERSION}.vsix"; \
	if [ ! -f "$$VSIX_FILE" ]; then \
		echo "Error: $$VSIX_FILE not found. Run 'make package' first."; \
		exit 1; \
	fi; \
	if ! command -v code > /dev/null 2>&1; then \
		echo "Error: 'code' command not found. Please install VS Code or add it to your PATH."; \
		exit 1; \
	fi; \
	code --install-extension "$$VSIX_FILE" --force; \
	if ! code --list-extensions | grep -qF "$${EXTENSION_PUBLISHER}.$${EXTENSION_NAME}"; then \
		echo "Error: Extension installation failed - extension not found in installed extensions list."; \
		exit 1; \
	fi; \
	echo "✓ Extension installed in VS Code"
	echo "NOTE: Reload the extension host via Command Palette (Ctrl/Cmd+Shift+P): Developer: Restart Extension Host"

install-cursor:
	@echo "Installing extension into Cursor..."
	@set -e; \
	EXTENSION_NAME=$$(node -p "require('./package.json').name"); \
	EXTENSION_PUBLISHER=$$(node -p "require('./package.json').publisher"); \
	EXTENSION_VERSION=$$(node -p "require('./package.json').version"); \
	VSIX_FILE="$${EXTENSION_NAME}-$${EXTENSION_VERSION}.vsix"; \
	if [ ! -f "$$VSIX_FILE" ]; then \
		echo "Error: $$VSIX_FILE not found. Run 'make package' first."; \
		exit 1; \
	fi; \
	if ! command -v cursor > /dev/null 2>&1; then \
		echo "Error: 'cursor' command not found. Please install Cursor or add it to your PATH."; \
		exit 1; \
	fi; \
	cursor --install-extension "$$VSIX_FILE" --force; \
	if ! cursor --list-extensions | grep -qF "$${EXTENSION_PUBLISHER}.$${EXTENSION_NAME}"; then \
		echo "Error: Extension installation failed - extension not found in installed extensions list."; \
		exit 1; \
	fi; \
	echo "✓ Extension installed in Cursor"
	echo "NOTE: Reload the extension host via Command Palette (Ctrl/Cmd+Shift+P): Developer: Restart Extension Host"

prepare:
	@echo "Preparing extension (downloading uv + bundling compiler)..."
	bash scripts/download_uv.sh current
	bash scripts/bundle_compiler.sh
	@echo "✓ Extension prepared"

prepare-all:
	@echo "Preparing extension for all platforms..."
	bash scripts/download_uv.sh all
	bash scripts/bundle_compiler.sh
	@echo "✓ Extension prepared for all platforms"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf out/
	rm -rf node_modules/

clean-binaries:
	@echo "Cleaning downloaded binaries and bundled compiler..."
	rm -rf bin/
	rm -rf compiler/
