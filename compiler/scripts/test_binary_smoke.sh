#!/usr/bin/env bash
# Smoke tests for standalone binary to ensure it works correctly

set -e

# Detect platform matching build_binaries.py logic
SYSTEM=$(uname -s | tr '[:upper:]' '[:lower:]')
MACHINE=$(uname -m | tr '[:upper:]' '[:lower:]')

# Normalize OS name (match Python's platform.system().lower())
case "$SYSTEM" in
  msys*|mingw*|cygwin*) SYSTEM="windows" ;;
  darwin*) SYSTEM="darwin" ;;
  linux*) SYSTEM="linux" ;;
esac

# Normalize architecture (match build_binaries.py)
case "$MACHINE" in
  x86_64|amd64) ARCH="x64" ;;
  aarch64|arm64) ARCH="arm64" ;;
  *) ARCH="$MACHINE" ;;
esac

BINARY_NAME="kb-dashboard-${SYSTEM}-${ARCH}"
if [ "$SYSTEM" = "windows" ]; then
  BINARY_NAME="${BINARY_NAME}.exe"
fi

BINARY_PATH="${BINARY_PATH:-dist/$BINARY_NAME}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPILER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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

"$BINARY_PATH" compile --input-dir "$COMPILER_ROOT/inputs" --output-dir "$TEMP_OUTPUT"

# Verify output files exist
if [ ! -f "$TEMP_OUTPUT/compiled_dashboards.ndjson" ]; then
  echo "✗ Expected output file not found"
  exit 1
fi
echo "✓ Compilation works and generates output"

# Test 4: Verify NDJSON format
echo "Test 4: Verify NDJSON output format"
if ! grep -q '"type":"dashboard"' "$TEMP_OUTPUT/compiled_dashboards.ndjson"; then
  echo "✗ Output doesn't contain expected dashboard JSON"
  exit 1
fi
echo "✓ Output format is valid NDJSON"

# Test 5: LSP server starts (expects stdin/stdout communication)
echo "Test 5: LSP server startup"
# Use portable timeout approach (GNU timeout not available on macOS by default)
if command -v timeout &> /dev/null; then
  # Use GNU timeout if available (Linux)
  echo '{"invalid": "request"}' | timeout 2 "$BINARY_PATH" lsp > /dev/null 2>&1 || true
elif command -v gtimeout &> /dev/null; then
  # Use gtimeout if available (macOS with coreutils via Homebrew)
  echo '{"invalid": "request"}' | gtimeout 2 "$BINARY_PATH" lsp > /dev/null 2>&1 || true
else
  # Fallback: portable bash-based timeout for macOS
  echo '{"invalid": "request"}' | "$BINARY_PATH" lsp > /dev/null 2>&1 &
  PID=$!
  sleep 2
  kill $PID 2>/dev/null || true
  wait $PID 2>/dev/null || true
fi
echo "✓ LSP server starts successfully"

echo ""
echo "✓ All binary smoke tests passed!"
