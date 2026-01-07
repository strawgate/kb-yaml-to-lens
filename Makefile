# Root Makefile - Global orchestration for all components
# Component-specific commands are in each component's Makefile

.PHONY: all help install ci check fix lint-all-check test-all clean clean-full lint-markdown lint-markdown-check inspector gh-get-review-threads gh-resolve-review-thread gh-get-latest-review gh-check-latest-review gh-get-comments-since gh-minimize-outdated-comments gh-check-repo-activity lint-python lint-python-check lint-yaml lint-yaml-check typecheck test test-coverage test-smoke test-links docs-build docs-build-quiet build-binary test-binary-smoke install-extension lint-extension lint-extension-check test-extension-python test-extension-typescript test-extension-e2e build-extension

all: ci

help:
	@echo "=== Root-Level Commands (Orchestration) ==="
	@echo ""
	@echo "Setup:"
	@echo "  install       - Install all component dependencies"
	@echo ""
	@echo "CI Workflow:"
	@echo "  all           - Run all CI checks (default target)"
	@echo "  ci            - Run CI checks across all components"
	@echo "  check         - Alias for ci"
	@echo "  fix           - Auto-fix linting issues across all components"
	@echo ""
	@echo "Linting:"
	@echo "  lint-all-check        - Check all linting without fixing"
	@echo "  lint-markdown         - Auto-fix markdown linting"
	@echo "  lint-markdown-check   - Check markdown without fixing"
	@echo "  lint-python           - Auto-fix Python linting (compiler)"
	@echo "  lint-python-check     - Check Python linting (compiler)"
	@echo "  lint-yaml             - Auto-fix YAML linting (compiler)"
	@echo "  lint-yaml-check       - Check YAML linting (compiler)"
	@echo "  lint-extension        - Lint VS Code extension"
	@echo "  lint-extension-check  - Check VS Code extension linting"
	@echo ""
	@echo "Type Checking:"
	@echo "  typecheck     - Run Python type checking (compiler)"
	@echo ""
	@echo "Testing:"
	@echo "  test-all                  - Run all tests across all components"
	@echo "  test                      - Run Python unit tests (compiler)"
	@echo "  test-coverage             - Run tests with coverage (compiler)"
	@echo "  test-smoke                - Run CLI smoke tests (compiler)"
	@echo "  test-links                - Check documentation links (compiler)"
	@echo "  test-extension-python     - Run Python tests (compiler)"
	@echo "  test-extension-typescript - Run TypeScript tests (extension)"
	@echo "  test-extension-e2e        - Run E2E tests (extension)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs-build        - Build documentation (compiler)"
	@echo "  docs-build-quiet  - Build documentation quietly (compiler)"
	@echo ""
	@echo "Building:"
	@echo "  build-binary          - Build standalone binary (compiler)"
	@echo "  test-binary-smoke     - Test standalone binary (compiler)"
	@echo "  build-extension       - Build VS Code extension"
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

install:
	@echo "Installing all component dependencies..."
	@echo ""
	@echo "→ Installing compiler dependencies..."
	@cd compiler && $(MAKE) install
	@echo ""
	@echo "→ Installing VS Code extension dependencies..."
	@cd vscode-extension && $(MAKE) install
	@echo ""
	@echo "→ Installing global tools..."
	@if command -v npm > /dev/null 2>&1; then \
		npm install -g markdownlint-cli; \
	else \
		echo "⚠ Skipping markdownlint-cli (npm not installed)"; \
	fi
	@echo ""
	@echo "✓ All dependencies installed"

ci:
	@echo "Running CI across all components..."
	@echo ""
	@echo "→ Running compiler CI..."
	@cd compiler && $(MAKE) ci
	@echo ""
	@echo "→ Running VS Code extension CI..."
	@if [ -d "vscode-extension/node_modules" ]; then \
		cd vscode-extension && $(MAKE) ci; \
	else \
		echo "⚠ Skipping VS Code extension (dependencies not installed)"; \
	fi
	@echo ""
	@echo "→ Checking markdown..."
	@$(MAKE) lint-markdown-check
	@echo ""
	@echo "✓ All CI checks passed!"

check: ci

fix:
	@echo "Auto-fixing linting issues across all components..."
	@echo ""
	@echo "→ Fixing compiler issues..."
	@cd compiler && $(MAKE) fix
	@echo ""
	@echo "→ Fixing VS Code extension issues..."
	@if [ -d "vscode-extension/node_modules" ]; then \
		cd vscode-extension && $(MAKE) fix; \
	else \
		echo "⚠ Skipping VS Code extension (dependencies not installed)"; \
	fi
	@echo ""
	@echo "→ Fixing markdown issues..."
	@$(MAKE) lint-markdown
	@echo ""
	@echo "✓ All fixes complete"

lint-all-check:
	@echo "Checking linting across all components..."
	@echo ""
	@echo "→ Checking compiler..."
	@cd compiler && $(MAKE) lint-check
	@echo ""
	@echo "→ Checking VS Code extension..."
	@if [ -d "vscode-extension/node_modules" ]; then \
		cd vscode-extension && $(MAKE) lint-check; \
	else \
		echo "⚠ Skipping VS Code extension (dependencies not installed)"; \
	fi
	@echo ""
	@echo "→ Checking markdown..."
	@$(MAKE) lint-markdown-check
	@echo ""
	@echo "✓ All linting checks passed"

test-all:
	@echo "Running tests across all components..."
	@echo ""
	@echo "→ Testing compiler..."
	@cd compiler && $(MAKE) test test-links test-smoke
	@echo ""
	@echo "→ Testing VS Code extension..."
	@if [ -d "vscode-extension/node_modules" ]; then \
		cd vscode-extension && $(MAKE) test; \
	else \
		echo "⚠ Skipping VS Code extension tests (dependencies not installed)"; \
	fi
	@echo ""
	@echo "→ Testing fixture generator..."
	@if docker images | grep -q "kibana-fixture-generator"; then \
		cd fixture-generator && $(MAKE) test; \
	else \
		echo "⚠ Skipping fixture generator tests (Docker image not built)"; \
	fi
	@echo ""
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
	@cd compiler && $(MAKE) clean
	@cd vscode-extension && $(MAKE) clean
	@cd fixture-generator && $(MAKE) clean

clean-full:
	@echo "Deep cleaning all components..."
	@cd compiler && $(MAKE) clean-full
	@cd vscode-extension && $(MAKE) clean
	@cd fixture-generator && $(MAKE) clean-image

# Helpers
inspector:
	@echo "Running MCP Inspector..."
	npx @modelcontextprotocol/inspector

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

# Compiler-specific commands (delegate to compiler/Makefile)
lint-python:
	@cd compiler && $(MAKE) lint-python

lint-python-check:
	@cd compiler && $(MAKE) lint-python-check

lint-yaml:
	@cd compiler && $(MAKE) lint-yaml

lint-yaml-check:
	@cd compiler && $(MAKE) lint-yaml-check

typecheck:
	@cd compiler && $(MAKE) typecheck

test:
	@cd compiler && $(MAKE) test

test-coverage:
	@cd compiler && $(MAKE) test-coverage

test-smoke:
	@cd compiler && $(MAKE) test-smoke

test-links:
	@cd compiler && $(MAKE) test-links

docs-build:
	@cd compiler && $(MAKE) docs-build

docs-build-quiet:
	@cd compiler && $(MAKE) docs-build-quiet

build-binary:
	@cd compiler && $(MAKE) build-binary

test-binary-smoke:
	@cd compiler && $(MAKE) test-binary-smoke

# VS Code extension commands (delegate to vscode-extension/Makefile)
install-extension:
	@cd vscode-extension && $(MAKE) install

lint-extension:
	@cd vscode-extension && $(MAKE) lint

lint-extension-check:
	@cd vscode-extension && $(MAKE) lint-check

test-extension-python:
	@cd compiler && $(MAKE) test

test-extension-typescript:
	@cd vscode-extension && $(MAKE) test-unit

test-extension-e2e:
	@cd vscode-extension && $(MAKE) test

build-extension:
	@cd vscode-extension && $(MAKE) compile

# Catch-all rule for script arguments
# IMPORTANT: This rule exists solely to prevent Make from treating arguments passed
# to GitHub helper scripts (e.g., "make gh-get-review-threads OWNER REPO PR") as
# undefined targets. All actual Make targets should be explicitly defined above.
# If a workflow is failing silently, check that the target exists above this line.
#
# WARNING: This rule makes undefined targets succeed silently. To prevent accidental
# silent failures, we check if the target looks like a make command (starts with
# common prefixes like lint-, test-, build-, etc.) and fail with an error if so.
%:
	@if echo "$@" | grep -qE '^(lint-|test-|build-|docs-|typecheck|compile|install-|clean-|ci|check|fix)'; then \
		echo "⚠️  ERROR: Target '$@' is not defined in Makefile" >&2; \
		echo "⚠️  Run 'make help' to see available commands" >&2; \
		exit 1; \
	fi
