# Building and Distributing the VS Code Extension

This guide covers building and packaging the VS Code extension with bundled LSP server binaries.

## Quick Start (Development)

For development, you don't need to build binaries:

```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VS Code to launch Extension Development Host
```

## Architecture

The extension uses a **hybrid distribution strategy**:

- **Production (VSIX)**: Bundles platform-specific LSP server binaries for zero-config installation
- **Development**: Falls back to local Python + `dashboard_compiler` package for easier development

### Binary Resolution

The `BinaryResolver` class (`src/binaryResolver.ts`) intelligently chooses the LSP server:

1. **Bundled Binary** (production): `bin/{platform}-{arch}/dashboard-compiler-lsp`
2. **Python Script** (development fallback): `python/compile_server.py`

Platform directories:

- `bin/linux-x64/` - Linux x86_64
- `bin/darwin-x64/` - macOS Intel
- `bin/darwin-arm64/` - macOS Apple Silicon
- `bin/win32-x64/` - Windows x86_64

## Building LSP Server Binaries

### Prerequisites

- Python 3.12+
- `pyinstaller` installed (`pip install pyinstaller`)
- `dashboard_compiler` package installed

### Build Binary for Current Platform

```bash
cd vscode-extension
npm run build-lsp-binary
```

This creates `bin/{platform}-{arch}/dashboard-compiler-lsp` for your current platform.

### Cross-Platform Builds

To build for all platforms, run the build script on each platform:

- **Linux x64**: Run on Ubuntu/Linux → creates `bin/linux-x64/dashboard-compiler-lsp`
- **macOS Intel**: Run on macOS Intel (GitHub Actions: macos-13) → creates `bin/darwin-x64/dashboard-compiler-lsp`
- **macOS ARM64**: Run on macOS ARM64 (GitHub Actions: macos-14) → creates `bin/darwin-arm64/dashboard-compiler-lsp`
- **Windows x64**: Run on Windows → creates `bin/win32-x64/dashboard-compiler-lsp.exe`

## Packaging the Extension

### Development VSIX (No Binaries)

For testing without binaries:

```bash
npm run package
```

Creates `yaml-dashboard-compiler-{version}.vsix` (works on all platforms, requires Python).

### Platform-Specific VSIX (With Binaries)

After building binaries, package for specific platforms:

```bash
# Package for specific platforms
npm run package:linux
npm run package:macos-x64
npm run package:macos-arm64
npm run package:windows
```

Creates platform-specific VSIX files:

- `yaml-dashboard-compiler-{version}@linux-x64.vsix`
- `yaml-dashboard-compiler-{version}@darwin-x64.vsix`
- `yaml-dashboard-compiler-{version}@darwin-arm64.vsix`
- `yaml-dashboard-compiler-{version}@win32-x64.vsix`

## Publishing to VS Code Marketplace

```bash
# Install vsce if needed
npm install -g @vscode/vsce

# Publish platform-specific versions
vsce publish --packagePath yaml-dashboard-compiler-{version}@linux-x64.vsix
vsce publish --packagePath yaml-dashboard-compiler-{version}@darwin-x64.vsix
vsce publish --packagePath yaml-dashboard-compiler-{version}@darwin-arm64.vsix
vsce publish --packagePath yaml-dashboard-compiler-{version}@win32-x64.vsix
```

VS Code Marketplace will automatically serve the correct VSIX based on the user's platform.

## CI/CD Integration Example

```yaml
# Build binaries on each platform
build-binaries:
  strategy:
    matrix:
      include:
        - os: ubuntu-latest
          platform: linux-x64
        - os: macos-13
          platform: darwin-x64
        - os: macos-14
          platform: darwin-arm64
        - os: windows-latest
          platform: win32-x64
  runs-on: ${{ matrix.os }}
  steps:
    - uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pyinstaller
    - name: Build LSP binary
      run: |
        cd vscode-extension
        npm run build-lsp-binary
    - name: Upload binary
      uses: actions/upload-artifact@v4
      with:
        name: lsp-binary-${{ matrix.platform }}
        path: vscode-extension/bin/

# Package extension for each platform
package:
  needs: build-binaries
  runs-on: ubuntu-latest
  strategy:
    matrix:
      platform: [linux-x64, darwin-x64, darwin-arm64, win32-x64]
  steps:
    - uses: actions/checkout@v4
    - name: Download binaries
      uses: actions/download-artifact@v4
      with:
        pattern: lsp-binary-*
        path: vscode-extension/bin/
        merge-multiple: true
    - name: Setup Node
      uses: actions/setup-node@v4
      with:
        node-version: '20'
    - name: Package extension
      run: |
        cd vscode-extension
        npm install
        npm run package:platform ${{ matrix.platform }}
    - name: Upload VSIX
      uses: actions/upload-artifact@v4
      with:
        name: vsix-${{ matrix.platform }}
        path: vscode-extension/*.vsix
```

## Directory Structure

```text
vscode-extension/
├── bin/                      # Bundled binaries (included in VSIX)
│   ├── linux-x64/
│   │   └── dashboard-compiler-lsp
│   ├── darwin-x64/
│   │   └── dashboard-compiler-lsp
│   ├── darwin-arm64/
│   │   └── dashboard-compiler-lsp
│   └── win32-x64/
│       └── dashboard-compiler-lsp.exe
├── python/                   # Python scripts (included in VSIX)
│   ├── compile_server.py     # LSP server (fallback)
│   ├── grid_extractor.py
│   └── grid_updater.py
├── scripts/                  # Build scripts (excluded from VSIX)
│   └── build_lsp_binary.py
├── src/                      # TypeScript source (excluded from VSIX)
│   ├── binaryResolver.ts
│   ├── compiler.ts
│   └── ...
└── out/                      # Compiled JS (included in VSIX)
```

## Troubleshooting

### Binary Not Found in Production

If extension falls back to Python in production:

1. Check binary exists: `ls vscode-extension/bin/{platform}-{arch}/dashboard-compiler-lsp`
2. Check binary is executable (Unix): `file vscode-extension/bin/{platform}/dashboard-compiler-lsp`
3. Verify `.vscodeignore` doesn't exclude `bin/`

### Python Not Found in Development

If development fallback fails:

1. Check `dashboard_compiler` installed: `python -c "import dashboard_compiler"`
2. Configure `yamlDashboard.pythonPath` in VS Code settings
3. Check extension logs: View → Output → "Dashboard Compiler LSP"
