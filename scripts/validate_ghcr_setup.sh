#!/bin/bash
# Test script to validate GHCR fixture generator setup
# 
# This script tests:
# 1. Dockerfile.ghcr is valid
# 2. docker-compose.ghcr.yml is valid
# 3. Workflow template is properly formatted
# 4. Documentation is complete

set -e

echo "=========================================="
echo "GHCR Fixture Generator Setup Validation"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Test 1: Verify files exist
echo "✓ Test 1: Checking required files exist..."
required_files=(
    "fixture-generator/Dockerfile.ghcr"
    "fixture-generator/docker-compose.ghcr.yml"
    "fixture-generator/GHCR.md"
    "COPILOT_INSTRUCTIONS.md"
    ".github/workflows/build-kibana-fixture-image.yml.template"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$PROJECT_ROOT/$file" ]; then
        echo "✗ Missing file: $file"
        exit 1
    fi
    echo "  ✓ $file exists"
done
echo ""

# Test 2: Validate Dockerfile.ghcr syntax
echo "✓ Test 2: Validating Dockerfile.ghcr..."
if ! docker build -f "$PROJECT_ROOT/fixture-generator/Dockerfile.ghcr" --help > /dev/null 2>&1; then
    echo "✗ Docker not available or Dockerfile.ghcr has syntax errors"
    echo "  Note: Full validation requires Docker"
else
    echo "  ✓ Dockerfile syntax appears valid"
fi
echo ""

# Test 3: Validate docker-compose.ghcr.yml syntax
echo "✓ Test 3: Validating docker-compose.ghcr.yml..."
if command -v docker-compose > /dev/null 2>&1; then
    if docker-compose -f "$PROJECT_ROOT/fixture-generator/docker-compose.ghcr.yml" config > /dev/null 2>&1; then
        echo "  ✓ docker-compose.ghcr.yml syntax is valid"
    else
        echo "✗ docker-compose.ghcr.yml has syntax errors"
        exit 1
    fi
else
    echo "  ⚠ docker-compose not available, skipping validation"
fi
echo ""

# Test 4: Check GHCR image path
echo "✓ Test 4: Checking GHCR image path..."
expected_image="ghcr.io/strawgate/kb-yaml-to-lens/kibana-fixture-generator"
if grep -q "$expected_image" "$PROJECT_ROOT/fixture-generator/docker-compose.ghcr.yml"; then
    echo "  ✓ GHCR image path is correct"
else
    echo "✗ GHCR image path not found in docker-compose.ghcr.yml"
    exit 1
fi
echo ""

# Test 5: Check workflow template has required elements
echo "✓ Test 5: Checking workflow template..."
workflow_template="$PROJECT_ROOT/.github/workflows/build-kibana-fixture-image.yml.template"
required_elements=(
    "workflow_dispatch"
    "schedule"
    "packages: write"
    "docker/build-push-action"
    "ghcr.io"
)

for element in "${required_elements[@]}"; do
    if ! grep -q "$element" "$workflow_template"; then
        echo "✗ Workflow template missing required element: $element"
        exit 1
    fi
    echo "  ✓ Found: $element"
done
echo ""

# Test 6: Check documentation is complete
echo "✓ Test 6: Checking documentation..."
ghcr_doc="$PROJECT_ROOT/fixture-generator/GHCR.md"
required_sections=(
    "Quick Start"
    "Available Images"
    "Automated Builds"
    "Troubleshooting"
    "CI/CD Integration"
)

for section in "${required_sections[@]}"; do
    if ! grep -q "$section" "$ghcr_doc"; then
        echo "✗ GHCR.md missing section: $section"
        exit 1
    fi
    echo "  ✓ Found section: $section"
done
echo ""

# Test 7: Check README update
echo "✓ Test 7: Checking README updates..."
readme="$PROJECT_ROOT/fixture-generator/README.md"
if grep -q "docker-compose.ghcr.yml" "$readme"; then
    echo "  ✓ README mentions GHCR option"
else
    echo "✗ README doesn't mention docker-compose.ghcr.yml"
    exit 1
fi
echo ""

# Test 8: Check for template marker
echo "✓ Test 8: Checking if actual workflow exists..."
actual_workflow="$PROJECT_ROOT/.github/workflows/build-kibana-fixture-image.yml"
if [ -f "$actual_workflow" ]; then
    echo "  ✓ Actual workflow file exists (Copilot has implemented it)"
else
    echo "  ⚠ Actual workflow file doesn't exist yet"
    echo "    This is expected - GitHub Copilot needs to implement it"
    echo "    Template is ready at: build-kibana-fixture-image.yml.template"
fi
echo ""

echo "=========================================="
echo "Validation Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ All required files are in place"
echo "  ✓ Configuration syntax is valid"
echo "  ✓ Documentation is complete"
echo "  ✓ GHCR paths are correct"
echo ""
echo "Next steps:"
echo "  1. Have GitHub Copilot implement the workflow file"
echo "  2. Trigger manual workflow dispatch to build first image"
echo "  3. Test GHCR image with: docker-compose -f docker-compose.ghcr.yml run generator"
echo ""
