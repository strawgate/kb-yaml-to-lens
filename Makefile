# Root Makefile - Global orchestration for all components
# Component-specific commands are in each component's Makefile

# Set SHELL before including Makefile.shared to ensure bash is used
# On Windows in GitHub Actions, bash is available via Git Bash when shell: bash is used
# GitHub Actions sets RUNNER_OS environment variable (Windows, Linux, macOS)
ifdef RUNNER_OS
  ifeq ($(RUNNER_OS),Windows)
    SHELL := bash
    MAKE_SHELL := bash
  else
    SHELL := /bin/bash
    MAKE_SHELL := /bin/bash
  endif
else
  # Not in GitHub Actions - default to /bin/bash for Unix-like systems
  SHELL := /bin/bash
  MAKE_SHELL := /bin/bash
endif

# Include shared helpers (after setting SHELL)
include Makefile.shared

# Detect OS and set appropriate shell for recursive make calls

# Components for pass-through commands
COMPONENTS := packages/kb-dashboard-cli packages/kb-dashboard-core packages/kb-dashboard-lint packages/kb-dashboard-tools packages/vscode-extension

# YAML linting exclusions
YAMLFIX_EXCLUDE := \
	--exclude ".venv/**/*.yaml" --exclude ".venv/**/*.yml" \
	--exclude "packages/kb-dashboard-cli/.venv/**/*.yaml" --exclude "packages/kb-dashboard-cli/.venv/**/*.yml" \
	--exclude "packages/kb-dashboard-core/.venv/**/*.yaml" --exclude "packages/kb-dashboard-core/.venv/**/*.yml" \
	--exclude "packages/kb-dashboard-lint/.venv/**/*.yaml" --exclude "packages/kb-dashboard-lint/.venv/**/*.yml" \
	--exclude "packages/kb-dashboard-tools/.venv/**/*.yaml" --exclude "packages/kb-dashboard-tools/.venv/**/*.yml" \
	--exclude "node_modules/**/*.yaml" --exclude "node_modules/**/*.yml" \
	--exclude "packages/vscode-extension/node_modules/**/*.yaml" --exclude "packages/vscode-extension/node_modules/**/*.yml" \
	--exclude "packages/vscode-extension/.vscode-test/**/*.yaml" --exclude "packages/vscode-extension/.vscode-test/**/*.yml"

.PHONY: help all root ci fix install lint-markdown lint-markdown-check lint-yaml lint-yaml-check bump-patch bump-minor bump-major bump-version-show check-merge-conflicts release-tag cli lint tools vscode docs gh

help:
	@echo "Root Makefile - Global Commands"
	@echo ""
	@echo "=== Component Pass-Through Commands ==="
	@echo ""
	@echo "Run target in all components:"
	@echo "  make all <target>       - Run in cli + core + lint + tools + vscode"
	@echo ""
	@echo "Run target in single component:"
	@echo "  make cli <target>       - Run in packages/kb-dashboard-cli/"
	@echo "  make core <target>      - Run in packages/kb-dashboard-core/"
	@echo "  make lint <target>      - Run in packages/kb-dashboard-lint/"
	@echo "  make tools <target>     - Run in packages/kb-dashboard-tools/"
	@echo "  make vscode <target>    - Run in packages/vscode-extension/"
	@echo "  make docs <target>      - Run in packages/kb-dashboard-docs/"
	@echo "  make gh <target>        - Run in .github/scripts/"
	@echo ""
	@echo "Common Examples:"
	@echo "  make all install          - Install root + all component dependencies"
	@echo "  make all ci               - Run CI checks (root linting + all components)"
	@echo "  make all fix              - Auto-fix linting (root + all components)"
	@echo "  make all clean            - Clean all components"
	@echo "  make root ci              - Run root-level CI checks (markdown + YAML lint)"
	@echo "  make root fix             - Auto-fix root-level linting"
	@echo "  make root install         - Install root-level dependencies"
	@echo "  make cli test-e2e         - Run CLI E2E tests (includes Docker tests if available)"
	@echo "  make vscode test-e2e      - Run VS Code E2E tests"
	@echo "  make docs ci              - Check docs (markdown lint + links)"
	@echo "  make docs serve           - Start docs server"
	@echo "  make gh help              - Show GitHub helper commands"
	@echo ""
	@echo "=== Global Linting ==="
	@echo ""
	@echo "  lint-markdown       - Auto-fix markdown issues"
	@echo "  lint-markdown-check - Check markdown without fixing"
	@echo "  lint-yaml           - Auto-fix YAML issues"
	@echo "  lint-yaml-check     - Check YAML without fixing"
	@echo ""
	@echo "=== Version Bumping ==="
	@echo ""
	@echo "  bump-patch         - Bump patch version (x.y.Z)"
	@echo "  bump-minor         - Bump minor version (x.Y.0)"
	@echo "  bump-major         - Bump major version (X.0.0)"
	@echo "  bump-version-show  - Show current version"
	@echo ""
	@echo "=== Release ==="
	@echo ""
	@echo "  release-tag        - Create and push git tag from pyproject.toml version"
	@echo ""
	@echo "=== Git Helpers ==="
	@echo ""
	@echo "  check-merge-conflicts [branch] - Check for merge conflicts with branch (default: origin/main)"

# Root-level targets (run linting checks)
root-ci:
	$(call print_start, "Running root-level CI checks")
	@echo ""
	@$(MAKE) lint-markdown-check
	@echo ""
	@$(MAKE) lint-yaml-check
	@echo ""
	$(call print_end, "Root-level CI checks passed")

root-fix:
	$(call print_start, "Running root-level lint fixes")
	@echo ""
	@$(MAKE) lint-markdown
	@echo ""
	@$(MAKE) lint-yaml
	@echo ""
	$(call print_end, "Root-level lint fixes complete")

root-install:
	$(call print_start, "Installing root-level dependencies")
	@if command -v npm > /dev/null 2>&1; then \
		if ! command -v markdownlint > /dev/null 2>&1; then \
			npm install -g markdownlint-cli $(INDENT); \
			printf "✓ markdownlint-cli installed\n"; \
		else \
			printf "✓ markdownlint-cli already installed\n"; \
		fi; \
	else \
		echo "⚠ npm not found - markdownlint-cli will not be installed"; \
		echo "  Install Node.js to enable markdown linting"; \
	fi
	$(call print_end, "Root-level dependencies installed")

# Root passthrough (allows "make root <target>")
root:
	@target="$(_ARGS)"; \
	if [ -z "$$target" ]; then \
		echo "Usage: make root <target>"; \
		echo "Available targets: ci, fix, install"; \
		exit 1; \
	fi; \
	$(MAKE) root-$$target

# Run target across root + all components
# Usage: make all <target>
all:
	@target="$(filter-out $@,$(MAKECMDGOALS))"; \
	if [ -z "$$target" ]; then \
		echo "Usage: make all <target>"; \
		echo "Example: make all clean"; \
		exit 1; \
	fi; \
	if [ "$$target" = "ci" ] || [ "$$target" = "fix" ] || [ "$$target" = "install" ]; then \
		printf "Root\n"; \
		$(MAKE) root-$$target || exit 1; \
		echo ""; \
	fi; \
	for component in $(COMPONENTS); do \
		printf "Component: %s\n" "$$component"; \
		$(MAKE) SHELL=$(MAKE_SHELL) -C $$component $$target || exit 1; \
	done; \
	printf "✓ All components: %s complete\n" "$$target"

# Markdown linting (global)
lint-markdown:
	$(call run_cmd, "Running markdownlint --fix", markdownlint --fix -c .markdownlint.jsonc ., "Markdown linting complete")

lint-markdown-check:
	$(call run_cmd, "Running markdownlint", markdownlint -c .markdownlint.jsonc ., "Markdown checks passed")

# YAML linting (global)
lint-yaml:
	$(call run_cmd, "Running yamlfix", uv run --group dev yamlfix $(YAMLFIX_EXCLUDE) ., "YAML linting complete")

lint-yaml-check:
	$(call run_cmd, "Running yamlfix --check", uv run --group dev yamlfix --check $(YAMLFIX_EXCLUDE) ., "YAML checks passed")

# Version bumping
BUMP_VERSION_SCRIPT := uv run scripts/bump-version.py

bump-patch:
	@$(BUMP_VERSION_SCRIPT) patch

bump-minor:
	@$(BUMP_VERSION_SCRIPT) minor

bump-major:
	@$(BUMP_VERSION_SCRIPT) major

bump-version-show:
	@$(BUMP_VERSION_SCRIPT) show

# Release
release-tag:
	@VERSION=$$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"); \
	TAG="v$$VERSION"; \
	echo "Current version: $$VERSION"; \
	echo "Creating tag: $$TAG"; \
	if git rev-parse "$$TAG" >/dev/null 2>&1; then \
		echo "Error: Tag $$TAG already exists"; \
		exit 1; \
	fi; \
	git tag -a "$$TAG" -m "Release $$VERSION"; \
	echo "Tag $$TAG created"; \
	echo "Pushing tag to origin..."; \
	git push origin "$$TAG"; \
	echo "✓ Tag $$TAG pushed successfully"

# Git helpers
check-merge-conflicts:
	@bash scripts/check-merge-conflicts.sh $(filter-out $@,$(MAKECMDGOALS))

# Component pass-through targets
# This hack prevents the parent Makefile from trying to execute the arguments
# as its own targets after passing them to sub-makes.
# For each pass-through target, we extract the remaining arguments and turn them
# into do-nothing targets using $(eval).
#
# Note: If arguments match existing root targets (e.g., "help"), Make will print
# "overriding commands for target" warnings. These warnings are expected and harmless.
# To suppress them, pipe the make command: make cli help 2>/dev/null
_FIRST_GOAL := $(firstword $(MAKECMDGOALS))

ifeq ($(_FIRST_GOAL),cli)
  _ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(_ARGS):;@:)
endif


ifeq ($(_FIRST_GOAL),vscode)
  _ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(_ARGS):;@:)
endif

ifeq ($(_FIRST_GOAL),docs)
  _ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(_ARGS):;@:)
endif

ifeq ($(_FIRST_GOAL),gh)
  _ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(_ARGS):;@:)
endif

ifeq ($(_FIRST_GOAL),lint)
  _ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(_ARGS):;@:)
endif

ifeq ($(_FIRST_GOAL),core)
  _ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(_ARGS):;@:)
endif

ifeq ($(_FIRST_GOAL),tools)
  _ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(_ARGS):;@:)
endif

ifeq ($(_FIRST_GOAL),root)
  _ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(_ARGS):;@:)
endif

cli:
	@$(MAKE) SHELL=$(MAKE_SHELL) -C packages/kb-dashboard-cli $(_ARGS)

core:
	@$(MAKE) SHELL=$(MAKE_SHELL) -C packages/kb-dashboard-core $(_ARGS)

lint:
	@$(MAKE) SHELL=$(MAKE_SHELL) -C packages/kb-dashboard-lint $(_ARGS)

tools:
	@$(MAKE) SHELL=$(MAKE_SHELL) -C packages/kb-dashboard-tools $(_ARGS)

vscode:
	@$(MAKE) SHELL=$(MAKE_SHELL) -C packages/vscode-extension $(_ARGS)

docs:
	@$(MAKE) SHELL=$(MAKE_SHELL) -C packages/kb-dashboard-docs $(_ARGS)

gh:
	@$(MAKE) SHELL=$(MAKE_SHELL) -C .github/scripts $(_ARGS)

# Prevent make from trying to build targets passed as arguments to 'all'
# Without this, 'make all clean' would try to run 'clean' after the all target completes
ifeq ($(_FIRST_GOAL),all)
  _ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(_ARGS):;@:)
endif

ifeq ($(_FIRST_GOAL),check-merge-conflicts)
  _ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(_ARGS):;@:)
endif
