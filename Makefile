# Root Makefile - Global orchestration for all components
# Component-specific commands are in each component's Makefile

# Enable parallel execution for check target (3 components)
# Use `make check PARALLEL=0` to disable parallel execution for debugging
PARALLEL ?= 1
ifeq ($(PARALLEL),1)
MAKEFLAGS += --jobs=3 --output-sync=target
endif

.PHONY: all help install ci check fix test-unit test-e2e test-smoke clean clean-full lint-markdown lint-markdown-check docs-serve docs-build docs-build-quiet docs-build-strict docs-deploy check-docs inspector prepare-extension prepare-extension-all package-extension package-extension-all install-extension-vscode install-extension-cursor gh-get-review-threads gh-resolve-review-thread gh-get-latest-review gh-check-latest-review gh-get-comments-since gh-minimize-outdated-comments gh-check-repo-activity bump-patch bump-minor bump-major bump-version-show compiler-ci vscode-ci markdown-ci compiler vscode docs

all: check

help:
	@echo "=== Root-Level Commands (Orchestration) ==="
	@echo ""
	@echo "Setup:"
	@echo "  install       - Install all component dependencies"
	@echo ""
	@echo "CI Workflow:"
	@echo "  all           - Run fast checks (default target, alias for check)"
	@echo "  check         - Run fast checks in parallel (lint + typecheck + unit tests)"
	@echo "  check PARALLEL=0 - Run checks sequentially (for debugging)"
	@echo "  ci            - Run comprehensive CI (check + e2e tests, matches GitHub Actions)"
	@echo "  fix           - Auto-fix linting issues across all components"
	@echo ""
	@echo "Linting:"
	@echo "  lint-markdown     - Auto-fix markdown linting"
	@echo "  lint-markdown-check - Check markdown without fixing"
	@echo ""
	@echo "Testing:"
	@echo "  test-unit     - Run unit tests only (fast)"
	@echo "  test-e2e      - Run end-to-end tests (requires setup)"
	@echo "  test-smoke    - Run CLI smoke tests"
	@echo ""
	@echo "Documentation:"
	@echo "  docs-serve         - Start local documentation server"
	@echo "  docs-build         - Build documentation static site"
	@echo "  docs-build-quiet   - Build documentation (errors only)"
	@echo "  docs-build-strict  - Build documentation with strict mode (fails on warnings)"
	@echo "  docs-deploy        - Deploy documentation to GitHub Pages"
	@echo "  check-docs         - Check documentation (lint + link verification)"
	@echo ""
	@echo "VS Code Extension:"
	@echo "  prepare-extension            - Download uv + bundle compiler (current platform, for dev)"
	@echo "  prepare-extension-all        - Download uv for all platforms + bundle compiler (for release)"
	@echo "  package-extension            - Prepare and package extension (current platform)"
	@echo "  package-extension-all        - Prepare and package extension (all platforms, for release)"
	@echo "  install-extension-vscode     - Package and install into VS Code"
	@echo "  install-extension-cursor     - Package and install into Cursor"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean         - Clean cache and temporary files"
	@echo "  clean-full    - Clean all including virtual environments"
	@echo ""
	@echo "Helpers:"
	@echo "  inspector     - Run MCP Inspector"
	@echo ""
	@echo "GitHub Workflow Helpers:"
	@echo "  gh-get-review-threads        - Get PR review threads (OWNER REPO PR [AUTHOR])"
	@echo "  gh-resolve-review-thread     - Resolve review thread (OWNER REPO PR THREAD_ID [COMMENT])"
	@echo "  gh-get-latest-review         - Get latest review from author (OWNER REPO PR AUTHOR)"
	@echo "  gh-check-latest-review       - Check if review is latest (OWNER REPO PR AUTHOR REVIEW_ID)"
	@echo "  gh-get-comments-since        - Get comments since timestamp (OWNER REPO ISSUE SINCE [AUTHOR])"
	@echo "  gh-minimize-outdated-comments - Minimize outdated PR comments (OWNER REPO PR)"
	@echo "  gh-check-repo-activity       - Check repo activity (OWNER REPO SINCE [THRESHOLD])"
	@echo ""
	@echo "Release:"
	@echo "  bump-patch        - Bump patch version across all components"
	@echo "  bump-minor        - Bump minor version across all components"
	@echo "  bump-major        - Bump major version across all components"
	@echo "  bump-version-show - Show current versions across all components"
	@echo ""
	@echo "=== Component Pass-Through Commands ==="
	@echo ""
	@echo "Run any target in a component's Makefile directly:"
	@echo "  make compiler <target>  - Run target in compiler/ (e.g., make compiler test)"
	@echo "  make vscode <target>    - Run target in vscode-extension/ (e.g., make vscode lint)"
	@echo "  make docs <target>      - Run target in docs/ (e.g., make docs test-links)"
	@echo ""
	@echo "Examples:"
	@echo "  make compiler help      - Show compiler-specific targets"
	@echo "  make vscode test-e2e    - Run VS Code extension E2E tests"
	@echo "  make compiler docker-build - Build compiler Docker image"

# Component iteration helper
# Run target in component
define run-in-component
	@echo "→ Running $(2) in $(1)..."
	@cd $(1) && $(MAKE) $(2)
	@echo ""
endef

install:
	@echo "Installing all component dependencies..."
	@echo ""
	$(call run-in-component,compiler,install)
	$(call run-in-component,vscode-extension,install)
	@echo "→ Installing global tools..."
	@if command -v npm > /dev/null 2>&1; then \
		npm install -g markdownlint-cli; \
	else \
		echo "⚠ Skipping markdownlint-cli (npm not installed)"; \
	fi
	@echo ""
	@echo "✓ All dependencies installed"

# Component CI targets for parallel execution
# Use `make check -j3` for parallel execution, `make check` for sequential
compiler-ci:
	@echo "→ Running compiler CI..."
	@cd compiler && $(MAKE) ci
	@echo ""

vscode-ci:
	@echo "→ Running vscode-extension CI..."
	@cd vscode-extension && $(MAKE) ci
	@echo ""

markdown-ci:
	@echo "→ Checking markdown..."
	@$(MAKE) lint-markdown-check
	@echo ""

check: compiler-ci vscode-ci markdown-ci
	@echo "✓ All fast checks passed!"

ci: check test-e2e
	@echo "✓ Comprehensive CI checks passed (matches GitHub Actions)!"

fix:
	@echo "Auto-fixing linting issues across all components..."
	@echo ""
	$(call run-in-component,compiler,fix)
	$(call run-in-component,vscode-extension,fix)
	@echo "→ Fixing markdown issues..."
	@$(MAKE) lint-markdown
	@echo ""
	@echo "✓ All fixes complete"

test-unit:
	@echo "Running unit tests across all components..."
	@echo ""
	$(call run-in-component,compiler,test)
	$(call run-in-component,vscode-extension,test-unit)
	@echo "✓ All unit tests passed"

test-e2e:
	@echo "Running end-to-end tests..."
	@echo ""
	$(call run-in-component,vscode-extension,test-e2e)
	@echo "✓ E2E tests passed"

test-smoke:
	@echo "Running smoke tests..."
	@echo ""
	$(call run-in-component,compiler,test-smoke)
	@echo "✓ Smoke tests passed"

# Markdown linting (global)
lint-markdown:
	@echo "Running markdownlint --fix..."
	markdownlint --fix -c .markdownlint.jsonc .

lint-markdown-check:
	@echo "Running markdownlint..."
	@markdownlint -c .markdownlint.jsonc . > /dev/null 2>&1 && echo "✓ Markdown checks passed" || (markdownlint -c .markdownlint.jsonc . && exit 1)

# Cleaning
clean:
	@echo "Cleaning all components..."
	@echo ""
	$(call run-in-component,compiler,clean)
	$(call run-in-component,vscode-extension,clean)
	@echo "✓ Cleaning complete"

clean-full:
	@echo "Deep cleaning all components..."
	@echo ""
	$(call run-in-component,compiler,clean-full)
	$(call run-in-component,vscode-extension,clean)
	@echo "✓ Deep cleaning complete"

# Helpers
inspector:
	@echo "Running MCP Inspector..."
	npx @modelcontextprotocol/inspector

# Documentation
docs-serve:
	@echo "Starting documentation server..."
	@cd docs && NO_COLOR=1 uv run --group docs mkdocs serve

docs-build:
	@echo "Building documentation..."
	@cd docs && NO_COLOR=1 uv run --group docs mkdocs build

docs-build-quiet:
	@echo "Building documentation (errors only)..."
	@cd docs && NO_COLOR=1 uv run --group docs mkdocs build --quiet --strict && echo "✓ Documentation builds successfully"

docs-build-strict:
	@echo "Building documentation with strict mode..."
	@cd docs && NO_COLOR=1 uv run --group docs mkdocs build --strict
	@echo "✓ Documentation builds successfully (strict mode)"

docs-deploy:
	@echo "Deploying documentation to GitHub Pages..."
	@cd docs && NO_COLOR=1 uv run --group docs mkdocs gh-deploy --force

check-docs:
	@echo "Checking documentation (lint + links)..."
	@echo ""
	@$(MAKE) lint-markdown-check
	@$(call run-in-component,docs,test-links)
	@echo ""
	@echo "✓ Documentation checks passed"

# VS Code Extension
prepare-extension:
	@echo "Preparing VS Code extension (download uv + bundle compiler)..."
	@echo ""
	$(call run-in-component,vscode-extension,prepare)
	@echo "✓ Extension prepared"

prepare-extension-all:
	@echo "Preparing VS Code extension for all platforms..."
	@echo ""
	$(call run-in-component,vscode-extension,prepare-all)
	@echo "✓ Extension prepared for all platforms"

package-extension: prepare-extension
	@echo "Packaging VS Code extension..."
	@echo ""
	$(call run-in-component,vscode-extension,package)
	@echo "✓ Extension packaged"

package-extension-all: prepare-extension-all
	@echo "Packaging VS Code extension (all platforms)..."
	@echo ""
	$(call run-in-component,vscode-extension,ci)
	$(call run-in-component,vscode-extension,package)
	@echo "✓ Extension packaged for all platforms"

install-extension-vscode: package-extension
	@echo "Installing extension into VS Code..."
	@echo ""
	$(call run-in-component,vscode-extension,install-vscode)

install-extension-cursor: package-extension
	@echo "Installing extension into Cursor..."
	@echo ""
	$(call run-in-component,vscode-extension,install-cursor)

# GitHub Workflow Helper Commands
gh-get-review-threads:
	@.github/scripts/gh-get-review-threads.sh $(filter-out $@,$(MAKECMDGOALS))

gh-resolve-review-thread:
	@.github/scripts/gh-resolve-review-thread.sh $(filter-out $@,$(MAKECMDGOALS))

gh-get-latest-review:
	@.github/scripts/gh-get-latest-review.sh $(filter-out $@,$(MAKECMDGOALS))

gh-check-latest-review:
	@.github/scripts/gh-check-latest-review.sh $(filter-out $@,$(MAKECMDGOALS))

gh-get-comments-since:
	@.github/scripts/gh-get-comments-since.sh $(filter-out $@,$(MAKECMDGOALS))

gh-minimize-outdated-comments:
	@.github/scripts/gh-minimize-outdated-comments.sh $(filter-out $@,$(MAKECMDGOALS))

gh-check-repo-activity:
	@.github/scripts/gh-check-repo-activity.sh $(filter-out $@,$(MAKECMDGOALS))

# Version bumping
bump-patch:
	@uv run scripts/bump-version.py patch

bump-minor:
	@uv run scripts/bump-version.py minor

bump-major:
	@uv run scripts/bump-version.py major

bump-version-show:
	@uv run scripts/bump-version.py show

# Component pass-through targets
# These allow running any target in a component's Makefile directly from the root
# Example: `make compiler test` runs `make test` in compiler/
compiler:
	@cd compiler && $(MAKE) $(filter-out $@,$(MAKECMDGOALS))

vscode:
	@cd vscode-extension && $(MAKE) $(filter-out $@,$(MAKECMDGOALS))

docs:
	@cd docs && $(MAKE) $(filter-out $@,$(MAKECMDGOALS))

# Prevent make from trying to build targets passed as arguments to scripts
%:
	@:
