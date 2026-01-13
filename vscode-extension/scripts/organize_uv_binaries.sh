#!/usr/bin/env bash
# Organize uv binaries from CI artifacts into platform-specific directories.
# Used in CI after downloading uv binary artifacts from the reusable workflow.
#
# Usage: organize_uv_binaries.sh [source_dir]
#   source_dir: Directory containing uv-{platform}/ subdirectories (default: uv-binaries)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$EXTENSION_ROOT/bin"

# Source directory containing downloaded artifacts
SOURCE_DIR="${1:-uv-binaries}"

# Platform configurations
PLATFORMS=(
    "linux-x64"
    "darwin-x64"
    "darwin-arm64"
    "win32-x64"
)

# Binary name per platform
declare -A BINARY_NAMES=(
    ["linux-x64"]="uv"
    ["darwin-x64"]="uv"
    ["darwin-arm64"]="uv"
    ["win32-x64"]="uv.exe"
)

echo "Organizing uv binaries from $SOURCE_DIR..."

COPIED=0
MISSING=0

for PLATFORM in "${PLATFORMS[@]}"; do
    BINARY_NAME="${BINARY_NAMES[$PLATFORM]}"
    SOURCE_PATH="$SOURCE_DIR/uv-$PLATFORM/$BINARY_NAME"
    TARGET_DIR="$BIN_DIR/$PLATFORM"
    TARGET_PATH="$TARGET_DIR/$BINARY_NAME"

    echo "Platform: $PLATFORM"
    echo "  Source: $SOURCE_PATH"
    echo "  Target: $TARGET_PATH"

    if [[ -f "$SOURCE_PATH" ]]; then
        mkdir -p "$TARGET_DIR"
        cp "$SOURCE_PATH" "$TARGET_PATH"

        # Make executable (for non-Windows)
        if [[ "$PLATFORM" != "win32-x64" ]]; then
            chmod +x "$TARGET_PATH"
        fi

        SIZE_KB=$(du -k "$TARGET_PATH" | cut -f1)
        echo "  ✓ Copied (${SIZE_KB}KB)"
        COPIED=$((COPIED + 1))
    else
        echo "  ⚠ Missing binary at $SOURCE_PATH"
        MISSING=$((MISSING + 1))
    fi
    echo ""
done

echo "Summary: Copied $COPIED binaries, $MISSING missing"

if [[ $MISSING -gt 0 ]]; then
    echo "Error: Some uv binaries were not found"
    exit 1
fi

echo "✓ All uv binaries organized successfully"
