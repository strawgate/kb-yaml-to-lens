# Building and Distributing the VS Code Extension

This guide covers building and packaging the VS Code extension with bundled LSP server binaries.

## Quick Start

### Development (No Binary Build Needed)

```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VS Code to launch Extension Development Host
```

The extension will automatically fall back to using Python + the `dashboard_compiler` package.

### Building LSP Binary (Current Platform)

```bash
cd vscode-extension
npm run build-lsp-binary
```

Creates `bin/{platform}-{arch}/kb-dashboard-compiler-lsp` for your current platform.

**Prerequisites**: Python 3.12+, pyinstaller (`pip install pyinstaller`), dashboard_compiler package installed

### Creating Platform-Specific VSIX

```bash
# Build binary first (see above), then:
npm run package:linux        # Linux x64
npm run package:macos-x64    # macOS Intel
npm run package:macos-arm64  # macOS Apple Silicon
npm run package:windows      # Windows x64
```

Creates `kb-dashboard-compiler-{version}@{platform}.vsix` files ready for distribution.

## How It Works

### Binary Resolution Strategy

The `BinaryResolver` class intelligently chooses the LSP server:

1. **Production**: Bundled binary at `bin/{platform}-{arch}/kb-dashboard-compiler-lsp`
2. **Development**: Falls back to Python module `dashboard_compiler.lsp.server`

Platform directories:

- `bin/linux-x64/` - Linux x86_64
- `bin/darwin-x64/` - macOS Intel
- `bin/darwin-arm64/` - macOS Apple Silicon
- `bin/win32-x64/` - Windows x86_64

### What Gets Bundled

- ✅ **LSP server binary**: Compiled from `src/dashboard_compiler/lsp/server.py` using PyInstaller
- ✅ **Compiled TypeScript**: JavaScript output in `out/` directory
- ❌ **Grid scripts**: Not bundled - require Python runtime (used by grid editor feature)

## Cross-Platform Builds

To build for all platforms, run the build script on each target platform:

| Platform | GitHub Actions Runner | Creates |
| -------- | --------------------- | ------- |
| Linux x64 | `ubuntu-latest` | `bin/linux-x64/kb-dashboard-compiler-lsp` |
| macOS Intel | `macos-13` | `bin/darwin-x64/kb-dashboard-compiler-lsp` |
| macOS ARM64 | `macos-14` | `bin/darwin-arm64/kb-dashboard-compiler-lsp` |
| Windows x64 | `windows-latest` | `bin/win32-x64/kb-dashboard-compiler-lsp.exe` |

**Note**: PyInstaller can only create binaries for the platform it runs on (no cross-compilation).

## Publishing to VS Code Marketplace

```bash
# Install vsce if needed
npm install -g @vscode/vsce

# Publish all platform-specific versions
vsce publish --packagePath kb-dashboard-compiler-{version}@linux-x64.vsix
vsce publish --packagePath kb-dashboard-compiler-{version}@darwin-x64.vsix
vsce publish --packagePath kb-dashboard-compiler-{version}@darwin-arm64.vsix
vsce publish --packagePath kb-dashboard-compiler-{version}@win32-x64.vsix
```

VS Code Marketplace automatically serves the correct VSIX based on the user's platform.

## Troubleshooting

### Binary Build Fails

#### "pyinstaller not found"

```bash
pip install pyinstaller
```

#### "LSP server script not found"

```bash
# Install dashboard_compiler package
pip install -e .  # from repository root
```

### Binary Not Found in Production

If the extension falls back to Python in production:

1. Verify binary exists: `ls bin/{platform}-{arch}/kb-dashboard-compiler-lsp`
2. Check `.vscodeignore` doesn't exclude `bin/`
3. Verify binary is executable (Unix): `file bin/{platform}-{arch}/kb-dashboard-compiler-lsp`

### Package Size Too Small

If the VSIX is ~180kb instead of ~18MB, the binary wasn't included:

1. Ensure you ran `npm run build-lsp-binary` before packaging
2. Check that `bin/{platform}-{arch}/kb-dashboard-compiler-lsp` exists
3. Verify the binary is ~18MB: `ls -lh bin/{platform}-{arch}/kb-dashboard-compiler-lsp`

For more details on the architecture and development workflow, see [README.md](./README.md).
