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
	@echo "  make docs <target>      - Run in docs/"
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
compiler:
	@$(MAKE) -C packages/kb-dashboard-compiler $(filter-out $@,$(MAKECMDGOALS))

vscode:
	@$(MAKE) -C vscode-extension $(filter-out $@,$(MAKECMDGOALS))

docs:
	@$(MAKE) -C docs $(filter-out $@,$(MAKECMDGOALS))

gh:
	@$(MAKE) -C .github/scripts $(filter-out $@,$(MAKECMDGOALS))

# Prevent make from trying to build targets passed as arguments
%:
	@:
