# VSCode Extension Makefile
# Component-specific commands for the kb-dashboard-compiler extension

.PHONY: help all install ci check fix test test-unit compile watch lint lint-check package install-vscode install-cursor clean prepare prepare-all clean-binaries

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

ci: install
	$(MAKE) compile lint test-unit
	@echo "✓ VSCode extension CI checks passed"

check: ci

fix: install
	@echo "Auto-fixing ESLint issues..."
	npm run lint -- --fix

test: install
	@echo "Running VSCode extension tests..."
	npm test

test-unit: install
	@echo "Running TypeScript tests for VSCode extension..."
	npm run compile && npm run test:unit

compile: install
	@echo "Compiling TypeScript..."
	npm run compile

watch: install
	@echo "Starting watch mode..."
	npm run watch

lint: install
	@echo "Running ESLint..."
	npm run compile && npm run lint

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
