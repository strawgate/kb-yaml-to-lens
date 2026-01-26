# Documentation Makefile
# Commands for documentation development and verification

# Include shared helpers
include ../../Makefile.shared

.PHONY: help install ci check serve build test-links clean

help:
	@echo "Documentation Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install       - Install Python dependencies and markdownlint-cli (requires npm)"
	@echo ""
	@echo "CI and Verification:"
	@echo "  ci            - Run all doc checks (markdown lint + link verification)"
	@echo "  check         - Alias for ci"
	@echo "  test-links    - Check documentation links only"
	@echo ""
	@echo "Development:"
	@echo "  serve         - Start local documentation server"
	@echo "  build         - Build documentation static site (strict mode, fails on warnings)"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean         - Clean build artifacts"
	@echo ""

install:
	$(call print_start, "Installing documentation tools")
	@if command -v npm > /dev/null 2>&1; then \
		npm install -g markdownlint-cli $(INDENT); \
		printf "✓ markdownlint-cli installed\n"; \
	else \
		echo "⚠ npm not found - please install Node.js to use markdownlint"; \
		exit 1; \
	fi
	$(call run_cmd, "Installing documentation dependencies", uv sync --package kb-dashboard-docs --group dev, "Documentation dependencies installed")

ci:
	$(call print_start, "Checking documentation (lint + links)")
	@echo ""
	@$(MAKE) -C $(ROOT) lint-markdown-check
	@echo ""
	@$(MAKE) test-links
	@echo ""
	$(call print_end, "Documentation checks passed")

check: ci

serve:
	$(call print_start, "Starting documentation server")
	@printf "  (Press Ctrl+C to stop)\n"
	@NO_COLOR=1 uv run --group dev mkdocs serve

build:
	$(call run_cmd, "Building documentation", NO_COLOR=1 uv run --group dev mkdocs build --strict, "Documentation built")

test-links:
	$(call run_cmd, "Checking documentation links", uv run --group dev pytest --check-links content/ -o addopts="" --tb=line --no-header -q --check-links-ignore='.*llms.*\.txt$$', "Documentation links checked")

clean:
	$(call print_start, "Cleaning documentation build artifacts")
	@rm -rf site/ llms.txt llms-full.txt 2>/dev/null || true
	$(call print_end, "Clean complete")
