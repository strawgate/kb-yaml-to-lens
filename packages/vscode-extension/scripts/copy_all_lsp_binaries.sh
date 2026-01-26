#!/usr/bin/env bash
# Copy all pre-built LSP binaries from compiler dist/ to extension bin/ directories
# Used in CI where binaries for all platforms are built in previous step

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(dirname "$SCRIPT_DIR")"
PACKAGES_ROOT="$(dirname "$EXTENSION_ROOT")"
COMPILER_DIST="$PACKAGES_ROOT/kb-dashboard-cli/dist"

echo "Copying all LSP binaries from compiler dist/ to extension bin/"

# Platform list for VS Code extension targets
PLATFORMS=(
    "linux-x64"
    "darwin-x64"
    "darwin-arm64"
    "win32-x64"
)

# Binary name mapping (OS name in dist -> platform name in extension)
declare -A BINARY_NAMES=(
    ["linux-x64"]="kb-dashboard-compiler-lsp"
    ["darwin-x64"]="kb-dashboard-compiler-lsp"
    ["darwin-arm64"]="kb-dashboard-compiler-lsp"
    ["win32-x64"]="kb-dashboard-compiler-lsp.exe"
)

COPIED=0
MISSING=0

for PLATFORM in "${PLATFORMS[@]}"; do
    BINARY_NAME="${BINARY_NAMES[$PLATFORM]}"

    # Construct source path - binaries in dist/ don't have platform suffix, just the binary name
    SOURCE_PATH="$COMPILER_DIST/$BINARY_NAME"

    TARGET_DIR="$EXTENSION_ROOT/bin/$PLATFORM"
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

        SIZE_MB=$(du -m "$TARGET_PATH" | cut -f1)
        echo "  ✓ Copied (${SIZE_MB}MB)"
        COPIED=$((COPIED + 1))
    else
        echo "  ⚠ Missing binary at $SOURCE_PATH"
        MISSING=$((MISSING + 1))
    fi
    echo ""
done

echo "Summary: Copied $COPIED binaries, $MISSING missing"

if [[ $MISSING -gt 0 ]]; then
    echo "Warning: Some binaries were not found"
    exit 1
fi

echo "✓ All LSP binaries copied successfully"
