#!/bin/bash

# Setup script for kb-dashboard Chrome Extension
# Downloads required dependencies

set -e

echo "🚀 Setting up kb-dashboard Chrome Extension..."
echo ""

# Check if we're in the right directory
if [ ! -f "manifest.json" ]; then
    echo "❌ Error: manifest.json not found. Run this script from the extension directory."
    exit 1
fi

# Download js-yaml
echo "📦 Downloading js-yaml..."
mkdir -p lib
curl -sL -o lib/js-yaml.min.js https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js
echo "✓ js-yaml downloaded"

# Download Pyodide
echo "📦 Downloading Pyodide (this may take a while, ~15MB)..."
PYODIDE_VERSION="v0.29.1"
PYODIDE_BASE_URL="https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full"
PYODIDE_DIR="lib/pyodide"
mkdir -p "$PYODIDE_DIR"

# Download main pyodide.js file
echo "  Downloading pyodide.js..."
curl -sL -o "$PYODIDE_DIR/pyodide.js" "${PYODIDE_BASE_URL}/pyodide.js"

# Download required core files
echo "  Downloading core Pyodide files..."
curl -sL -o "$PYODIDE_DIR/pyodide.asm.js" "${PYODIDE_BASE_URL}/pyodide.asm.js"
curl -sL -o "$PYODIDE_DIR/pyodide.asm.wasm" "${PYODIDE_BASE_URL}/pyodide.asm.wasm"
curl -sL -o "$PYODIDE_DIR/pyodide.asm.data" "${PYODIDE_BASE_URL}/pyodide.asm.data"
curl -sL -o "$PYODIDE_DIR/packages.json" "${PYODIDE_BASE_URL}/packages.json"
curl -sL -o "$PYODIDE_DIR/repodata.json" "${PYODIDE_BASE_URL}/repodata.json"
curl -sL -o "$PYODIDE_DIR/pyodide-lock.json" "${PYODIDE_BASE_URL}/pyodide-lock.json"
curl -sL -o "$PYODIDE_DIR/python_stdlib.zip" "${PYODIDE_BASE_URL}/python_stdlib.zip"

# Download micropip (needed for installing packages)
echo "  Downloading micropip..."
curl -sL -o "$PYODIDE_DIR/micropip-0.11.0-py3-none-any.whl" "${PYODIDE_BASE_URL}/micropip-0.11.0-py3-none-any.whl"

# Download packaging (micropip dependency)
echo "  Downloading packaging..."
curl -sL -o "$PYODIDE_DIR/packaging-24.2-py3-none-any.whl" "${PYODIDE_BASE_URL}/packaging-24.2-py3-none-any.whl"

# Download pyyaml
echo "  Downloading pyyaml..."
curl -sL -o "$PYODIDE_DIR/pyyaml-6.0.2-cp313-cp313-pyodide_2025_0_wasm32.whl" "${PYODIDE_BASE_URL}/pyyaml-6.0.2-cp313-cp313-pyodide_2025_0_wasm32.whl"

# Download pydantic and its dependencies (required for the dashboard compiler)
# Versions from pyodide-lock.json for Pyodide v0.29.1
echo "  Downloading pydantic and dependencies..."
# typing_extensions
curl -sL -o "$PYODIDE_DIR/typing_extensions-4.15.0-py3-none-any.whl" "${PYODIDE_BASE_URL}/typing_extensions-4.15.0-py3-none-any.whl" || echo "  Warning: typing_extensions download failed"
# annotated_types
curl -sL -o "$PYODIDE_DIR/annotated_types-0.7.0-py3-none-any.whl" "${PYODIDE_BASE_URL}/annotated_types-0.7.0-py3-none-any.whl" || echo "  Warning: annotated_types download failed"
# pydantic_core (native dependency with Wasm build)
curl -sL -o "$PYODIDE_DIR/pydantic_core-2.27.2-cp313-cp313-pyodide_2025_0_wasm32.whl" "${PYODIDE_BASE_URL}/pydantic_core-2.27.2-cp313-cp313-pyodide_2025_0_wasm32.whl" || echo "  Warning: pydantic_core download failed"
# pydantic itself
curl -sL -o "$PYODIDE_DIR/pydantic-2.10.6-py3-none-any.whl" "${PYODIDE_BASE_URL}/pydantic-2.10.6-py3-none-any.whl" || echo "  Warning: pydantic download failed"

echo "✓ Pyodide downloaded"

# Download Monaco Editor (bundled locally for CSP compliance)
echo "📦 Downloading Monaco Editor..."
MONACO_VERSION="0.52.0"
MONACO_DIR="lib/monaco-editor"
mkdir -p "$MONACO_DIR"

# Download Monaco using npm pack and extract
echo "  Downloading Monaco package..."
cd lib
npm pack "monaco-editor@${MONACO_VERSION}" --silent 2>/dev/null || {
    echo "  npm not available, downloading from CDN..."
    curl -sL "https://registry.npmjs.org/monaco-editor/-/monaco-editor-${MONACO_VERSION}.tgz" -o monaco-editor.tgz
}
# Handle both possible filenames
if [ -f "monaco-editor-${MONACO_VERSION}.tgz" ]; then
    mv "monaco-editor-${MONACO_VERSION}.tgz" monaco-editor.tgz
fi
tar -xzf monaco-editor.tgz
mv package/min/vs monaco-editor/
rm -rf package monaco-editor.tgz
cd ..
echo "✓ Monaco Editor downloaded"

# Create placeholder icons if they don't exist
echo "🎨 Checking icons..."
if [ ! -f "icons/icon16.png" ] || [ ! -f "icons/icon48.png" ] || [ ! -f "icons/icon128.png" ]; then
    echo "⚠️  Warning: Icon files not found in icons/ directory"
    echo "   You'll need to add icon16.png, icon48.png, and icon128.png"
    echo "   Quick option: https://favicon.io/emoji-favicons/bar-chart/"
else
    echo "✓ Icons found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add icon files to icons/ directory (if not done)"
echo "2. Open Chrome and go to chrome://extensions/"
echo "3. Enable 'Developer mode'"
echo "4. Click 'Load unpacked' and select this directory"
echo "5. Click the extension icon to open the dashboard builder!"
echo ""
