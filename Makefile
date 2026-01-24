# Root Makefile - Global orchestration for all components
# Component-specific commands are in each component's Makefile

# Enable parallel execution for check target (3 components)
# Use `make check PARALLEL=0` to disable parallel execution for debugging
PARALLEL ?= 1
ifeq ($(PARALLEL),1)
MAKEFLAGS += --jobs=3 --output-sync=target
endif

.PHONY: all help install ci check fix test-unit test-e2e clean clean-full lint-markdown lint-markdown-check check-docs gh-get-review-threads gh-resolve-review-thread gh-get-latest-review gh-check-latest-review gh-get-comments-since gh-minimize-outdated-comments gh-check-repo-activity bump-patch bump-minor bump-major bump-version-show compiler-ci vscode-ci markdown-ci compiler vscode docs

all: check

help:
	@echo "=== Root Orchestration Commands ==="
	@echo ""
	@echo "  install       - Install all dependencies (compiler + vscode + markdownlint)"
	@echo "  check         - Run fast checks in parallel (lint + typecheck + unit tests)"
	@echo "  ci            - Run comprehensive CI (check + e2e tests)"
	@echo "  fix           - Auto-fix linting issues across all components"
	@echo "  test-unit     - Run unit tests across components"
	@echo "  test-e2e      - Run end-to-end tests"
	@echo "  clean         - Clean all component caches"
	@echo "  clean-full    - Clean all including virtual environments"
	@echo "  check-docs    - Check documentation (markdown lint + link verification)"
	@echo ""
	@echo "Markdown Linting (global):"
	@echo "  lint-markdown       - Auto-fix markdown issues"
	@echo "  lint-markdown-check - Check markdown without fixing"
	@echo ""
	@echo "=== Component Pass-Through Commands ==="
	@echo ""
	@echo "Run any component target directly from root:"
	@echo "  make compiler <target>  - Run in compiler/"
	@echo "  make vscode <target>    - Run in vscode-extension/"
	@echo "  make docs <target>      - Run in docs/"
	@echo ""
	@echo "Examples:"
	@echo "  make compiler help         - Show all compiler targets"
	@echo "  make compiler test-smoke   - Run compiler smoke tests"
	@echo "  make compiler docker-build - Build compiler Docker image"
	@echo "  make vscode help           - Show all vscode targets"
	@echo "  make vscode prepare        - Prepare extension for dev"
	@echo "  make vscode package        - Package extension"
	@echo "  make docs serve            - Start docs server"
	@echo "  make docs build            - Build documentation"
	@echo ""
	@echo "=== Release & GitHub Helpers ==="
	@echo ""
	@echo "Version bumping:"
	@echo "  bump-patch / bump-minor / bump-major / bump-version-show"
	@echo ""
	@echo "GitHub workflow helpers (for Claude Code Action):"
	@echo "  gh-get-review-threads / gh-resolve-review-thread / gh-get-latest-review"
	@echo "  gh-check-latest-review / gh-get-comments-since / gh-minimize-outdated-comments"
	@echo "  gh-check-repo-activity"

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

check-docs:
	@echo "Checking documentation (lint + links)..."
	@echo ""
	@$(MAKE) lint-markdown-check
	@$(call run-in-component,docs,test-links)
	@echo ""
	@echo "✓ Documentation checks passed"

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
