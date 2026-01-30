#!/usr/bin/env bash
# Bundle the compiler source code with the VS Code extension.
# The compiler is packaged alongside uv so the extension can run kb-dashboard via uv run.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$EXTENSION_ROOT")")"
COMPILER_SRC="$PROJECT_ROOT/packages/kb-dashboard-cli"
BUNDLE_DIR="$EXTENSION_ROOT/compiler"

echo "Bundling compiler source code..."

# Clean previous bundle
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"

# Copy essential files
cp "$COMPILER_SRC/pyproject.toml" "$BUNDLE_DIR/"
cp "$PROJECT_ROOT/uv.lock" "$BUNDLE_DIR/"
cp "$COMPILER_SRC/README.md" "$BUNDLE_DIR/"

# Copy source code
cp -r "$COMPILER_SRC/src" "$BUNDLE_DIR/src"

# Calculate bundle size
SIZE_KB=$(du -sk "$BUNDLE_DIR" | cut -f1)
echo "✓ Compiler bundled at $BUNDLE_DIR (${SIZE_KB}KB)"
