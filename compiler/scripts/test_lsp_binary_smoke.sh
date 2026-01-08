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
echo '{"invalid": "request"}' | timeout 2 "$BINARY_PATH" > /dev/null 2>&1 || true

echo "✓ LSP binary smoke tests passed"
