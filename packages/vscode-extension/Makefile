# VSCode Extension Makefile
# Component-specific commands for the kb-dashboard-compiler extension

.PHONY: help all install ci check fix test test-unit test-unit-only test-e2e test-e2e-only compile watch lint lint-check lint-only typecheck package install-vscode install-cursor clean prepare prepare-all generate-schemas check-schemas

# Include shared helpers
include ../../Makefile.shared

help:
	@echo "VSCode Extension Commands:"
	@echo ""
	@echo "Dependency Management:"
	@echo "  install          - Install npm dependencies"
	@echo ""
	@echo "CI and Development Workflow:"
	@echo "  all              - Default target (alias for ci)"
	@echo "  ci               - Run all CI checks (compile + lint + test)"
	@echo "  check            - Alias for ci"
	@echo "  fix              - Auto-fix linting issues"
	@echo ""
	@echo "Compilation:"
	@echo "  compile          - Compile TypeScript"
	@echo "  watch            - Watch mode for development"
	@echo ""
	@echo "Linting:"
	@echo "  lint             - Check linting (compiles first)"
	@echo "  lint-check       - Alias for lint"
	@echo "  lint-only        - Check linting (no compile, for CI)"
	@echo ""
	@echo "Type Checking:"
	@echo "  typecheck        - Run TypeScript type checking (no emit)"
	@echo ""
	@echo "Testing:"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-e2e         - Run E2E tests (compiles first)"
	@echo ""
	@echo "Packaging and Installation:"
	@echo "  package          - Create .vsix package"
	@echo "  install-vscode   - Install packaged extension into VS Code"
	@echo "  install-cursor   - Install packaged extension into Cursor"
	@echo ""
	@echo "Preparation:"
	@echo "  prepare          - Download uv + bundle compiler (current platform, for dev)"
	@echo "  prepare-all      - Download uv for all platforms + bundle compiler (for release)"
	@echo ""
	@echo "Schema Generation:"
	@echo "  generate-schemas - Generate Zod schemas from Pydantic models"
	@echo "  check-schemas    - Check if generated schemas are up to date"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean            - Clean build artifacts, dependencies, and binaries"

install:
	$(call run_cmd, "Installing VSCode extension dependencies", npm ci, "VSCode extension dependencies installed")

all: ci

ci: install compile
	$(call print_start, "Running linting and tests")
	$(MAKE) lint-only test-unit-only
	$(call print_end, "VSCode extension CI checks passed")

check: ci

fix: install
	$(call run_cmd, "Running ESLint --fix", npm run lint -- --fix, "TypeScript linting complete (with auto-fix)")

test: install
	$(call run_cmd, "Running VSCode extension tests", npm test, "VSCode extension tests passed")

# Non-compiling target for use in CI after compile has already run
test-unit-only:
	@if [ ! -d "out/test/unit" ] || [ -z "$$(find out/test/unit -name '*.test.js' 2>/dev/null | head -1)" ]; then \
		echo "Error: No unit tests found. Ensure tests are compiled with 'make compile'."; \
		exit 1; \
	fi
	$(call run_cmd, "Running TypeScript tests", ./node_modules/.bin/mocha out/test/unit/**/*.test.js --ui tdd, "Unit tests passed")

test-unit: install compile test-unit-only

# Non-compiling target for use in CI after compile has already run
test-e2e-only:
	$(call run_cmd, "Running VSCode extension E2E tests", node ./out/test/runTest.js, "E2E tests passed")

test-e2e: install compile test-e2e-only

compile: install
	$(call run_cmd, "Compiling TypeScript", npm run compile, "TypeScript compiled")

watch: install
	$(call print_start, "Starting watch mode")
	@printf "  (Press Ctrl+C to stop)\n"
	@npm run watch

# Non-compiling target for use in CI after compile has already run
lint-only:
	$(call run_cmd, "Running ESLint", npm run lint, "ESLint checks passed")

lint: install compile lint-only

lint-check: lint

typecheck: install
	$(call run_cmd, "Running TypeScript type checking", npx tsc --noEmit, "Type checking passed")

package: install
	$(call run_cmd, "Creating .vsix package", npm run package, ".vsix package created")

# Helper function to install extension into an editor
# Usage: $(call install_extension, "Editor Name", editor_command)
define install_extension
	$(call print_start, "Installing extension into $(1)")
	@set -e; \
	EXTENSION_NAME=$$(node -p "require('./package.json').name"); \
	EXTENSION_PUBLISHER=$$(node -p "require('./package.json').publisher"); \
	EXTENSION_VERSION=$$(node -p "require('./package.json').version"); \
	VSIX_FILE="$${EXTENSION_NAME}-$${EXTENSION_VERSION}.vsix"; \
	if [ ! -f "$$VSIX_FILE" ]; then \
		echo "Error: $$VSIX_FILE not found. Run 'make package' first."; \
		exit 1; \
	fi; \
	if ! command -v $(2) > /dev/null 2>&1; then \
		echo "Error: '$(2)' command not found. Please install $(1) or add it to your PATH."; \
		exit 1; \
	fi; \
	$(2) --install-extension "$$VSIX_FILE" --force; \
	if ! $(2) --list-extensions | grep -qF "$${EXTENSION_PUBLISHER}.$${EXTENSION_NAME}"; then \
		echo "Error: Extension installation failed - extension not found in installed extensions list."; \
		exit 1; \
	fi; \
	printf "✓ Extension installed in $(1)\n"; \
	echo "NOTE: Reload the extension host via Command Palette (Ctrl/Cmd+Shift+P): Developer: Restart Extension Host"
endef

install-vscode: package
	$(call install_extension, "VS Code", code)

install-cursor: package
	$(call install_extension, "Cursor", cursor)

# Helper function to prepare extension (download uv + bundle compiler)
# Usage: $(call prepare_extension, platform_description, platform_arg, success_message)
define prepare_extension
	$(call run_cmd, "Downloading uv for $(1)", bash scripts/download_uv.sh $(2), "uv downloaded")
	$(call run_cmd, "Bundling compiler", bash scripts/bundle_compiler.sh, "Compiler bundled")
	$(call print_end, $(3))
endef

prepare:
	$(call prepare_extension, "current platform", current, "Extension prepared")

prepare-all:
	$(call prepare_extension, "all platforms", all, "Extension prepared for all platforms")

# Schema Generation
generate-schemas:
	$(call run_cmd, "Generating Zod schemas from Pydantic models", bash scripts/generate_schemas.sh, "Schemas generated")

check-schemas:
	$(call print_start, "Checking if schemas are up to date")
	@cp src/schemas.generated.ts src/schemas.generated.ts.bak 2>/dev/null || true
	@bash scripts/generate_schemas.sh > /dev/null 2>&1
	@if ! diff -q src/schemas.generated.ts src/schemas.generated.ts.bak > /dev/null 2>&1; then \
		mv src/schemas.generated.ts.bak src/schemas.generated.ts 2>/dev/null || true; \
		echo "Error: Generated schemas are out of date. Run 'make generate-schemas' to update."; \
		exit 1; \
	fi
	@mv src/schemas.generated.ts.bak src/schemas.generated.ts 2>/dev/null || true
	$(call print_end, "Schemas are up to date")

clean:
	$(call print_start, "Cleaning build artifacts")
	@rm -rf out/ node_modules/ bin/ compiler/ *.vsix 2>/dev/null || true
	$(call print_end, "Build artifacts cleaned")