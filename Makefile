# Root Makefile - Global orchestration for all components
# Component-specific commands are in each component's Makefile

# Include shared helpers
include Makefile.shared

# Components for pass-through commands
COMPONENTS := packages/kb-dashboard-compiler vscode-extension

# YAML linting exclusions
YAMLFIX_EXCLUDE := \
	--exclude ".venv/**/*.yaml" --exclude ".venv/**/*.yml" \
	--exclude "packages/kb-dashboard-compiler/.venv/**/*.yaml" --exclude "packages/kb-dashboard-compiler/.venv/**/*.yml" \
	--exclude "node_modules/**/*.yaml" --exclude "node_modules/**/*.yml" \
	--exclude "vscode-extension/node_modules/**/*.yaml" --exclude "vscode-extension/node_modules/**/*.yml" \
	--exclude "vscode-extension/.vscode-test/**/*.yaml" --exclude "vscode-extension/.vscode-test/**/*.yml"

.PHONY: help all lint-markdown lint-markdown-check lint-yaml lint-yaml-check bump-patch bump-minor bump-major bump-version-show compiler vscode docs gh

help:
	@echo "Root Makefile - Global Commands"
	@echo ""
	@echo "=== Component Pass-Through Commands ==="
	@echo ""
	@echo "Run target in all components:"
	@echo "  make all <target>       - Run in compiler + vscode"
	@echo ""
	@echo "Run target in single component:"
	@echo "  make compiler <target>  - Run in packages/kb-dashboard-compiler/"
	@echo "  make vscode <target>    - Run in vscode-extension/"
	@echo "  make docs <target>      - Run in packages/kb-dashboard-docs/"
	@echo "  make gh <target>        - Run in .github/scripts/"
	@echo ""
	@echo "Common Examples:"
	@echo "  make all install          - Install all component dependencies"
	@echo "  make all ci               - Run CI checks in all components"
	@echo "  make all fix              - Auto-fix linting in all components"
	@echo "  make all clean            - Clean all components"
	@echo "  make compiler test-smoke  - Run compiler smoke tests"
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

# Run target across all components
# Usage: make all <target>
all:
	@target="$(filter-out $@,$(MAKECMDGOALS))"; \
	if [ -z "$$target" ]; then \
		echo "Usage: make all <target>"; \
		echo "Example: make all clean"; \
		exit 1; \
	fi; \
	for component in $(COMPONENTS); do \
		printf "▸ Component: %s\n" "$$component"; \
		$(MAKE) -C $$component $$target || exit 1; \
	done; \
	printf "✓ All components: %s complete\n" "$$target"

# Markdown linting (global)
lint-markdown:
	$(call run_cmd, "Running markdownlint --fix", markdownlint --fix -c .markdownlint.jsonc ., "Markdown linting complete")

lint-markdown-check:
	$(call print_start, "Running markdownlint")
	@markdownlint -c .markdownlint.jsonc . $(INDENT)
	$(call print_end, "Markdown checks passed")

# YAML linting (global)
lint-yaml:
	$(call run_cmd, "Running yamlfix", cd packages/kb-dashboard-compiler && uv run yamlfix $(YAMLFIX_EXCLUDE) ../.., "YAML linting complete")

lint-yaml-check:
	$(call print_start, "Running yamlfix --check")
	@cd packages/kb-dashboard-compiler && uv run yamlfix --check $(YAMLFIX_EXCLUDE) ../.. $(INDENT)
	$(call print_end, "YAML checks passed")

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

# Component pass-through targets
# This hack prevents the parent Makefile from trying to execute the arguments
# as its own targets after passing them to sub-makes.
# For each pass-through target, we extract the remaining arguments and turn them
# into do-nothing targets using $(eval).
#
# Note: If arguments match existing root targets (e.g., "help"), Make will print
# "overriding commands for target" warnings. These warnings are expected and harmless.
# To suppress them, pipe the make command: make compiler help 2>/dev/null
_FIRST_GOAL := $(firstword $(MAKECMDGOALS))

ifeq ($(_FIRST_GOAL),compiler)
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

compiler:
	@$(MAKE) -C packages/kb-dashboard-compiler $(_ARGS)

vscode:
	@$(MAKE) -C vscode-extension $(_ARGS)

docs:
	@$(MAKE) -C packages/kb-dashboard-docs $(_ARGS)

gh:
	@$(MAKE) -C .github/scripts $(_ARGS)
