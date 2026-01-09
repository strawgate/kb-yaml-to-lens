#!/usr/bin/env bash
# Copy unified binary from compiler dist/ to extension bin/ directory for current platform

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$EXTENSION_ROOT")"
COMPILER_DIST="$PROJECT_ROOT/compiler/dist"

# Detect and normalize platform
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$OS" in
  msys*|mingw*|cygwin*) OS="windows" ;;
  darwin*) OS="darwin" ;;
  linux*) OS="linux" ;;
esac

case "$ARCH" in
  x86_64|amd64) ARCH="x64" ;;
  aarch64|arm64) ARCH="arm64" ;;
esac

# Source binary uses Python platform naming
SOURCE_BINARY="kb-dashboard-${OS}-${ARCH}"
[[ "$OS" == "windows" ]] && SOURCE_BINARY="${SOURCE_BINARY}.exe"
SOURCE_PATH="$COMPILER_DIST/$SOURCE_BINARY"

# Target uses VS Code platform naming (windows -> win32)
TARGET_PLATFORM="${OS}-${ARCH}"
[[ "$OS" == "windows" ]] && TARGET_PLATFORM="win32-${ARCH}"

TARGET_BINARY="kb-dashboard"
[[ "$OS" == "windows" ]] && TARGET_BINARY="${TARGET_BINARY}.exe"
TARGET_DIR="$EXTENSION_ROOT/bin/$TARGET_PLATFORM"
TARGET_PATH="$TARGET_DIR/$TARGET_BINARY"

# Verify source exists
if [[ ! -f "$SOURCE_PATH" ]]; then
    echo "Error: Binary not found at $SOURCE_PATH"
    echo "Run 'cd compiler && make build-binary' first"
    exit 1
fi

# Copy binary
mkdir -p "$TARGET_DIR"
cp "$SOURCE_PATH" "$TARGET_PATH"
[[ "$OS" != "windows" ]] && chmod +x "$TARGET_PATH"

SIZE_MB=$(du -m "$TARGET_PATH" | cut -f1)
echo "✓ Copied unified binary (${SIZE_MB}MB) to $TARGET_PATH"
