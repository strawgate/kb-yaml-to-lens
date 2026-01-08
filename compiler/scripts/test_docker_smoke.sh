#!/usr/bin/env bash
# Smoke tests for Docker image to ensure it works correctly

set -e

IMAGE_NAME="${IMAGE_NAME:-kb-dashboard-compiler:latest}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPILER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Testing Docker image: $IMAGE_NAME"

# Test 1: Image exists and can run
echo "Test 1: Image runs and shows help"
docker run --rm "$IMAGE_NAME" --help > /dev/null
echo "✓ Help command works"

# Test 2: Version check
echo "Test 2: Version check"
docker run --rm "$IMAGE_NAME" --version > /dev/null
echo "✓ Version command works"

# Test 3: Compile sample YAML
echo "Test 3: Compile sample YAML"
TEMP_OUTPUT=$(mktemp -d)
trap 'rm -rf "$TEMP_OUTPUT"' EXIT

docker run --rm \
  -v "$COMPILER_ROOT/inputs:/inputs:ro" \
  -v "$TEMP_OUTPUT:/output" \
  "$IMAGE_NAME" \
  compile --input-dir /inputs --output-dir /output

# Verify output files exist
if [ ! -f "$TEMP_OUTPUT/esql-controls-example.ndjson" ]; then
  echo "✗ Expected output file not found"
  exit 1
fi
echo "✓ Compilation works and generates output"

# Test 4: Verify NDJSON format
echo "Test 4: Verify NDJSON output format"
if ! grep -q '"type":"dashboard"' "$TEMP_OUTPUT/esql-controls-example.ndjson"; then
  echo "✗ Output doesn't contain expected dashboard JSON"
  exit 1
fi
echo "✓ Output format is valid NDJSON"

echo ""
echo "✓ All Docker smoke tests passed!"
