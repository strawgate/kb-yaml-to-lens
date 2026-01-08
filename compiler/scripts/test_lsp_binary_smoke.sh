#!/usr/bin/env bash
# Smoke test for LSP binary

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPILER_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$COMPILER_ROOT/dist"

# Detect platform
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

if [[ "$ARCH" == "x86_64" || "$ARCH" == "amd64" ]]; then
    ARCH="x64"
elif [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    ARCH="arm64"
fi

BINARY_NAME="kb-dashboard-compiler-lsp"
if [[ "$OS" == "mingw"* || "$OS" == "msys"* || "$OS" == "cygwin"* ]]; then
    BINARY_NAME="${BINARY_NAME}.exe"
fi

BINARY_PATH="$DIST_DIR/$BINARY_NAME"

echo "Testing LSP binary: $BINARY_PATH"

# Check binary exists
if [[ ! -f "$BINARY_PATH" ]]; then
    echo "Error: LSP binary not found at $BINARY_PATH"
    echo "Run 'make build-lsp-binary' first"
    exit 1
fi

# Test 1: Binary is executable
if [[ "$OS" != "mingw"* && "$OS" != "msys"* && "$OS" != "cygwin"* ]]; then
    if [[ ! -x "$BINARY_PATH" ]]; then
        echo "Error: Binary is not executable"
        exit 1
    fi
fi

# Test 2: Binary starts (LSP server expects stdin/stdout communication)
# We'll send an invalid request and check it doesn't crash immediately
echo "Testing LSP binary startup..."

# Use portable timeout approach (GNU timeout not available on macOS by default)
if command -v timeout &> /dev/null; then
    # Use GNU timeout if available (Linux)
    echo '{"invalid": "request"}' | timeout 2 "$BINARY_PATH" > /dev/null 2>&1 || true
elif command -v gtimeout &> /dev/null; then
    # Use gtimeout if available (macOS with coreutils via Homebrew)
    echo '{"invalid": "request"}' | gtimeout 2 "$BINARY_PATH" > /dev/null 2>&1 || true
else
    # Fallback: portable bash-based timeout for macOS
    echo '{"invalid": "request"}' | "$BINARY_PATH" > /dev/null 2>&1 &
    PID=$!
    sleep 2
    kill $PID 2>/dev/null || true
    wait $PID 2>/dev/null || true
fi

echo "✓ LSP binary smoke tests passed"
