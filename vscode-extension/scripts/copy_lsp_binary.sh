#!/usr/bin/env bash
# Copy LSP binary from compiler dist/ to extension bin/ directory

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$EXTENSION_ROOT")"
COMPILER_DIST="$PROJECT_ROOT/compiler/dist"

# Detect platform
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

if [[ "$ARCH" == "x86_64" || "$ARCH" == "amd64" ]]; then
    ARCH="x64"
elif [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    ARCH="arm64"
fi

PLATFORM="${OS}-${ARCH}"
BINARY_NAME="kb-dashboard-compiler-lsp"
if [[ "$OS" == "mingw"* || "$OS" == "msys"* || "$OS" == "cygwin"* ]]; then
    BINARY_NAME="${BINARY_NAME}.exe"
fi

SOURCE_PATH="$COMPILER_DIST/$BINARY_NAME"
TARGET_DIR="$EXTENSION_ROOT/bin/$PLATFORM"
TARGET_PATH="$TARGET_DIR/$BINARY_NAME"

echo "Copying LSP binary for platform: $PLATFORM"
echo "  Source: $SOURCE_PATH"
echo "  Target: $TARGET_PATH"

# Check source exists
if [[ ! -f "$SOURCE_PATH" ]]; then
    echo "Error: LSP binary not found at $SOURCE_PATH"
    echo "Run 'cd compiler && make build-lsp-binary' first"
    exit 1
fi

# Create target directory
mkdir -p "$TARGET_DIR"

# Copy binary
cp "$SOURCE_PATH" "$TARGET_PATH"

# Make executable (Unix-like systems)
if [[ "$OS" != "mingw"* && "$OS" != "msys"* && "$OS" != "cygwin"* ]]; then
    chmod +x "$TARGET_PATH"
fi

SIZE_MB=$(du -m "$TARGET_PATH" | cut -f1)
echo "✓ Copied LSP binary (${SIZE_MB}MB) to $TARGET_PATH"
