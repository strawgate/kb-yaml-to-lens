# Root Makefile - Global orchestration for all components
# Component-specific commands are in each component's Makefile

.PHONY: all help install ci check fix lint-all-check test-all test-unit test-e2e clean clean-full lint-markdown lint-markdown-check docs-serve docs-build docs-build-quiet docs-deploy inspector build-extension-binaries package-extension gh-get-review-threads gh-resolve-review-thread gh-get-latest-review gh-check-latest-review gh-get-comments-since gh-minimize-outdated-comments gh-check-repo-activity

all: check

help:
	@echo "=== Root-Level Commands (Orchestration) ==="
	@echo ""
	@echo "Setup:"
	@echo "  install       - Install all component dependencies"
	@echo ""
	@echo "CI Workflow:"
	@echo "  all           - Run fast checks (default target, alias for check)"
	@echo "  check         - Run fast checks (lint + typecheck + unit tests)"
	@echo "  ci            - Run comprehensive CI (check + e2e tests, matches GitHub Actions)"
	@echo "  fix           - Auto-fix linting issues across all components"
	@echo ""
	@echo "Linting:"
	@echo "  lint-all-check    - Check all linting without fixing"
	@echo "  lint-markdown     - Auto-fix markdown linting"
	@echo "  lint-markdown-check - Check markdown without fixing"
	@echo ""
	@echo "Testing:"
	@echo "  test-unit     - Run unit tests only (fast)"
	@echo "  test-e2e      - Run end-to-end tests (requires setup)"
	@echo "  test-all      - Run all tests (unit + e2e + smoke)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs-serve    - Start local documentation server"
	@echo "  docs-build    - Build documentation static site"
	@echo "  docs-build-quiet - Build documentation (errors only)"
	@echo "  docs-deploy   - Deploy documentation to GitHub Pages"
	@echo ""
	@echo "VS Code Extension:"
	@echo "  build-extension-binaries - Build LSP binaries for extension (current platform)"
	@echo "  package-extension        - Package extension with binaries"
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
	@echo "=== Component-Specific Commands ==="
	@echo ""
	@echo "For component-specific commands, use:"
	@echo "  cd compiler/ && make help        - Compiler commands"
	@echo "  cd vscode-extension/ && make help - VS Code extension commands"
	@echo "  cd fixture-generator/ && make help - Fixture generator commands"

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

check:
	@echo "Running fast checks (lint + typecheck + unit tests)..."
	@echo ""
	$(call run-in-component,compiler,ci)
	$(call run-in-component,vscode-extension,ci)
	@echo "→ Checking markdown..."
	@$(MAKE) lint-markdown-check
	@echo ""
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

lint-all-check:
	@echo "Checking linting across all components..."
	@echo ""
	$(call run-in-component,compiler,lint-check)
	$(call run-in-component,vscode-extension,lint-check)
	@echo "→ Checking markdown..."
	@$(MAKE) lint-markdown-check
	@echo ""
	@echo "✓ All linting checks passed"

test-unit:
	@echo "Running unit tests across all components..."
	@echo ""
	$(call run-in-component,compiler,test)
	$(call run-in-component,vscode-extension,test-unit)
	@echo "✓ All unit tests passed"

test-e2e:
	@echo "Running end-to-end tests..."
	@echo ""
	$(call run-in-component,vscode-extension,test)
	@echo "✓ E2E tests passed"

test-all: test-unit test-e2e
	@echo "Running additional tests..."
	@echo ""
	$(call run-in-component,compiler,test-links)
	$(call run-in-component,compiler,test-smoke)
	$(call run-in-component,fixture-generator,test)
	@echo "✓ All tests passed"

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
	$(call run-in-component,fixture-generator,clean)
	@echo "✓ Cleaning complete"

clean-full:
	@echo "Deep cleaning all components..."
	@echo ""
	$(call run-in-component,compiler,clean-full)
	$(call run-in-component,vscode-extension,clean)
	$(call run-in-component,fixture-generator,clean-image)
	@echo "✓ Deep cleaning complete"

# Helpers
inspector:
	@echo "Running MCP Inspector..."
	npx @modelcontextprotocol/inspector

# Documentation
docs-serve:
	@echo "Starting documentation server..."
	NO_COLOR=1 uv run --group docs mkdocs serve

docs-build:
	@echo "Building documentation..."
	NO_COLOR=1 uv run --group docs mkdocs build

docs-build-quiet:
	@echo "Building documentation (errors only)..."
	@NO_COLOR=1 uv run --group docs mkdocs build --quiet --strict && echo "✓ Documentation builds successfully"

docs-deploy:
	@echo "Deploying documentation to GitHub Pages..."
	NO_COLOR=1 uv run --group docs mkdocs gh-deploy --force

# VS Code Extension
build-extension-binaries:
	@echo "Building LSP binaries for VS Code extension..."
	@echo ""
	$(call run-in-component,compiler,build-lsp-binary)
	$(call run-in-component,vscode-extension,copy-lsp-binary)
	@echo "✓ Extension binaries ready"

package-extension: build-extension-binaries
	@echo "Packaging VS Code extension..."
	@echo ""
	$(call run-in-component,vscode-extension,package)
	@echo "✓ Extension packaged"

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

# Prevent make from trying to build targets passed as arguments to scripts
%:
	@:
