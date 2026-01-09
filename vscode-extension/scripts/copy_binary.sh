#!/usr/bin/env bash
# Copy unified binary from compiler dist/ to extension bin/ directory

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$EXTENSION_ROOT")"
COMPILER_DIST="$PROJECT_ROOT/compiler/dist"

# Detect platform
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

# Normalize OS name (match Python's platform.system().lower())
case "$OS" in
  msys*|mingw*|cygwin*) OS="windows" ;;
  darwin*) OS="darwin" ;;
  linux*) OS="linux" ;;
esac

# Normalize architecture (match build_binaries.py)
case "$ARCH" in
  x86_64|amd64) ARCH="x64" ;;
  aarch64|arm64) ARCH="arm64" ;;
esac

PLATFORM="${OS}-${ARCH}"
BINARY_NAME="kb-dashboard-${PLATFORM}"
if [[ "$OS" == "windows" ]]; then
    BINARY_NAME="${BINARY_NAME}.exe"
fi

SOURCE_PATH="$COMPILER_DIST/$BINARY_NAME"

# Target uses different naming convention for platform directory
TARGET_PLATFORM="${OS}-${ARCH}"
if [[ "$OS" == "windows" ]]; then
    TARGET_PLATFORM="win32-${ARCH}"
fi

TARGET_DIR="$EXTENSION_ROOT/bin/$TARGET_PLATFORM"
TARGET_BINARY_NAME="kb-dashboard"
if [[ "$OS" == "windows" ]]; then
    TARGET_BINARY_NAME="${TARGET_BINARY_NAME}.exe"
fi
TARGET_PATH="$TARGET_DIR/$TARGET_BINARY_NAME"

echo "Copying unified binary for platform: $PLATFORM"
echo "  Source: $SOURCE_PATH"
echo "  Target: $TARGET_PATH"

# Check source exists
if [[ ! -f "$SOURCE_PATH" ]]; then
    echo "Error: Unified binary not found at $SOURCE_PATH"
    echo "Run 'cd compiler && make build-binary' first"
    exit 1
fi

# Create target directory
mkdir -p "$TARGET_DIR"

# Copy binary
cp "$SOURCE_PATH" "$TARGET_PATH"

# Make executable (Unix-like systems)
if [[ "$OS" != "windows" ]]; then
    chmod +x "$TARGET_PATH"
fi

SIZE_MB=$(du -m "$TARGET_PATH" | cut -f1)
echo "✓ Copied unified binary (${SIZE_MB}MB) to $TARGET_PATH"
