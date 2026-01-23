# Documentation Makefile
# Commands for documentation development and verification

.PHONY: help serve build build-strict test-links clean

help:
	@echo "Documentation Commands:"
	@echo ""
	@echo "Development:"
	@echo "  serve         - Start local documentation server"
	@echo "  build         - Build documentation static site"
	@echo "  build-strict  - Build with strict mode (fails on warnings)"
	@echo ""
	@echo "Verification:"
	@echo "  test-links    - Check documentation links"
	@echo ""
	@echo "Cleaning:"
	@echo "  clean         - Clean build artifacts"
	@echo ""

serve:
	@echo "Starting documentation server..."
	NO_COLOR=1 uv run --group docs mkdocs serve

build:
	@echo "Building documentation..."
	NO_COLOR=1 uv run --group docs mkdocs build

build-strict:
	@echo "Building documentation with strict mode..."
	NO_COLOR=1 uv run --group docs mkdocs build --strict
	@echo "✓ Documentation builds successfully (strict mode)"

test-links:
	@echo "Checking documentation links..."
	@cd ../compiler && uv run pytest --check-links ../docs/content/ README.md ../CONTRIBUTING.md -o addopts="" --tb=line --no-header -q --check-links-ignore='.*llms.*\.txt$$'

clean:
	@echo "Cleaning documentation build artifacts..."
	rm -rf site/
	@echo "✓ Clean complete"
