#!/usr/bin/env bash
# Bundle the compiler source code with the VS Code extension.
# The compiler is packaged alongside uv so the extension can run kb-dashboard via uv run.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(dirname "$SCRIPT_DIR")"
PACKAGES_ROOT="$(dirname "$EXTENSION_ROOT")"
PROJECT_ROOT="$(dirname "$PACKAGES_ROOT")"
BUNDLE_DIR="$EXTENSION_ROOT/packages"

echo "Bundling compiler packages..."

# Clean previous bundle
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"

# Copy workspace pyproject.toml
cp "$PACKAGES_ROOT/pyproject.toml" "$BUNDLE_DIR/"

# Copy each package
for pkg in kb-dashboard-core kb-dashboard-cli kb-dashboard-lsp kb-dashboard-tools kb-dashboard-compiler; do
    if [ -d "$PACKAGES_ROOT/$pkg" ]; then
        echo "  Bundling $pkg..."
        cp -r "$PACKAGES_ROOT/$pkg" "$BUNDLE_DIR/"
    fi
done

# Copy root uv.lock if it exists
if [ -f "$PROJECT_ROOT/uv.lock" ]; then
    cp "$PROJECT_ROOT/uv.lock" "$BUNDLE_DIR/"
fi

# Calculate bundle size
SIZE_KB=$(du -sk "$BUNDLE_DIR" | cut -f1)
echo "✓ Compiler packages bundled at $BUNDLE_DIR (${SIZE_KB}KB)"
