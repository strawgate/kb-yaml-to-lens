#!/usr/bin/env bash
# Smoke tests for LSP binary used by VS Code extension

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPILER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Detect platform for Windows .exe extension
SYSTEM=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$SYSTEM" in
  msys*|mingw*|cygwin*) SYSTEM="windows" ;;
esac

BINARY_NAME="kb-dashboard-compiler-lsp"
if [ "$SYSTEM" = "windows" ]; then
  BINARY_NAME="${BINARY_NAME}.exe"
fi

BINARY_PATH="${BINARY_PATH:-$COMPILER_ROOT/dist/$BINARY_NAME}"

if [ ! -f "$BINARY_PATH" ]; then
  echo "Error: Binary not found at $BINARY_PATH"
  echo "Please build the binary first with: make build-lsp-binary"
  exit 1
fi

echo "Testing LSP binary: $BINARY_PATH"

# Make binary executable
chmod +x "$BINARY_PATH" 2>/dev/null || true

# Test 1: Binary runs and shows help
echo "Test 1: Binary runs and shows help"
"$BINARY_PATH" --help > /dev/null
echo "OK: Help command works"

# Test 2: Version check
echo "Test 2: Version check"
"$BINARY_PATH" --version > /dev/null
echo "OK: Version command works"

# Test 3: LSP server responds to initialization
echo "Test 3: LSP server responds to initialization"
TEMP_LSP_LOG=$(mktemp)
trap 'rm -f "$TEMP_LSP_LOG"' EXIT

# Valid LSP initialize request (Content-Length required for LSP protocol)
INIT_REQUEST='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}'
CONTENT_LENGTH=${#INIT_REQUEST}
LSP_TIMEOUT_SECONDS=${LSP_TIMEOUT_SECONDS:-5}

if command -v timeout &> /dev/null; then
  printf "Content-Length: %d\r\n\r\n%s" "$CONTENT_LENGTH" "$INIT_REQUEST" | timeout "$LSP_TIMEOUT_SECONDS" "$BINARY_PATH" lsp > "$TEMP_LSP_LOG" 2>&1 || true
elif command -v gtimeout &> /dev/null; then
  printf "Content-Length: %d\r\n\r\n%s" "$CONTENT_LENGTH" "$INIT_REQUEST" | gtimeout "$LSP_TIMEOUT_SECONDS" "$BINARY_PATH" lsp > "$TEMP_LSP_LOG" 2>&1 || true
else
  printf "Content-Length: %d\r\n\r\n%s" "$CONTENT_LENGTH" "$INIT_REQUEST" | "$BINARY_PATH" lsp > "$TEMP_LSP_LOG" 2>&1 &
  PID=$!
  # Poll for process completion instead of sleeping full duration
  for _ in $(seq 1 "$LSP_TIMEOUT_SECONDS"); do
    if ! kill -0 "$PID" 2>/dev/null; then
      break
    fi
    sleep 1
  done
  kill "$PID" 2>/dev/null || true
  wait "$PID" 2>/dev/null || true
fi

# Check if LSP server responded with valid JSON-RPC response
if grep -Eq '"error"\s*:' "$TEMP_LSP_LOG"; then
  echo "Error: LSP server returned an error response"
  cat "$TEMP_LSP_LOG"
  exit 1
elif grep -Eq '"jsonrpc"\s*:\s*"2\.0"' "$TEMP_LSP_LOG" && \
   grep -Eq '"id"\s*:\s*1' "$TEMP_LSP_LOG" && \
   grep -Eq '"result"\s*:' "$TEMP_LSP_LOG"; then
  echo "OK: LSP server responds correctly to initialize request"
else
  echo "Error: LSP server did not respond correctly"
  cat "$TEMP_LSP_LOG"
  exit 1
fi

echo ""
echo "All LSP binary smoke tests passed!"
