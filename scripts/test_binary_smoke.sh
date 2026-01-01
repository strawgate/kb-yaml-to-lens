#!/usr/bin/env bash
# Smoke tests for standalone binary to ensure it works correctly

set -e

BINARY_PATH="${BINARY_PATH:-dist/kb-dashboard-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m | sed 's/x86_64/x64/' | sed 's/aarch64/arm64/')}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Add .exe extension for Windows
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
  BINARY_PATH="${BINARY_PATH}.exe"
fi

if [ ! -f "$BINARY_PATH" ]; then
  echo "✗ Binary not found at $BINARY_PATH"
  echo "Please build the binary first with: make build-binary"
  exit 1
fi

echo "Testing binary: $BINARY_PATH"

# Make binary executable
chmod +x "$BINARY_PATH" 2>/dev/null || true

# Test 1: Binary runs and shows help
echo "Test 1: Binary runs and shows help"
"$BINARY_PATH" --help > /dev/null
echo "✓ Help command works"

# Test 2: Version check
echo "Test 2: Version check"
"$BINARY_PATH" --version > /dev/null
echo "✓ Version command works"

# Test 3: Compile sample YAML
echo "Test 3: Compile sample YAML"
TEMP_OUTPUT=$(mktemp -d)
trap 'rm -rf "$TEMP_OUTPUT"' EXIT

"$BINARY_PATH" compile --input-dir "$PROJECT_ROOT/inputs" --output-dir "$TEMP_OUTPUT"

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
echo "✓ All binary smoke tests passed!"
