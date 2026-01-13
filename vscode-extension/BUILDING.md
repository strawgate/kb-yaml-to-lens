# Building and Distributing the VS Code Extension

This guide covers building and packaging the VS Code extension with bundled uv + compiler source.

## Quick Start

### Development (No Binary Build Needed)

```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VS Code to launch Extension Development Host
```

The extension will automatically fall back to using Python + the `dashboard_compiler` package.

### Building for Current Platform

```bash
# From repository root
make prepare-extension       # Download uv + bundle compiler for current platform
make package-extension       # Prepare and package

# Or from vscode-extension directory
cd vscode-extension
make prepare                 # Download uv + bundle compiler
make package                 # Create .vsix
```

Creates:

- `bin/{platform}/uv` - Platform-specific uv binary
- `compiler/` - Bundled compiler source (pyproject.toml, uv.lock, src/)
- `.vsix` package ready for installation

**Prerequisites**: Node.js 20+, npm

### Building for All Platforms (Release)

```bash
# From repository root
make prepare-extension-all   # Download uv for all platforms + bundle compiler
make package-extension-all   # Run CI checks and package

# Or from vscode-extension directory
cd vscode-extension
make prepare-all             # Download uv for all platforms + bundle compiler
```

## How It Works

### Binary Resolution Strategy

The `BinaryResolver` class intelligently chooses the execution method:

1. **Production**: Bundled uv + compiler source
   - Uses: `uv run --directory <compiler> kb-dashboard <subcommand>`
   - Fast dependency resolution via lockfile
2. **Development**: Falls back to Python module `dashboard_compiler.lsp.server`

Platform directories:

- `bin/linux-x64/uv` - Linux x86_64
- `bin/darwin-x64/uv` - macOS Intel
- `bin/darwin-arm64/uv` - macOS Apple Silicon
- `bin/win32-x64/uv.exe` - Windows x86_64

### Build Process

1. **Download uv binary**: `scripts/download_uv.sh` downloads the platform-specific uv binary from GitHub releases
2. **Bundle compiler source**: `scripts/bundle_compiler.sh` copies compiler source (pyproject.toml, uv.lock, src/) to extension
3. **Packaging**: When creating VSIX packages, both uv and compiler are bundled

At runtime, `uv run --directory <compiler> kb-dashboard` uses the lockfile to ensure reproducible execution without pre-building wheels.

### What Gets Bundled

- ✅ **uv binary**: Platform-specific executable (~20MB)
- ✅ **Compiler source**: pyproject.toml, uv.lock, src/ (~200KB)
- ✅ **Compiled TypeScript**: JavaScript output in `out/` directory
- ❌ **Python virtualenv**: Created at first run by uv

## Cross-Platform Builds

The `download_uv.sh` script handles platform-specific downloads:

| Platform | Directory | Binary |
| -------- | --------- | ------ |
| Linux x64 | `bin/linux-x64/` | `uv` |
| macOS Intel | `bin/darwin-x64/` | `uv` |
| macOS ARM64 | `bin/darwin-arm64/` | `uv` |
| Windows x64 | `bin/win32-x64/` | `uv.exe` |

```bash
# Download for specific platform
./scripts/download_uv.sh linux-x64
./scripts/download_uv.sh darwin-arm64

# Download for all platforms
./scripts/download_uv.sh all

# Download for current platform only
./scripts/download_uv.sh current
```

## Publishing to VS Code Marketplace

```bash
# Install vsce if needed
npm install -g @vscode/vsce

# Publish (after running make package-extension-all)
vsce publish --packagePath kb-dashboard-compiler-{version}.vsix
```

VS Code Marketplace automatically serves the correct VSIX based on the user's platform.

## Troubleshooting

### Extension Falls Back to Python

If the extension falls back to Python in production:

1. Verify uv exists: `ls bin/{platform}/uv`
2. Verify compiler bundled: `ls compiler/pyproject.toml`
3. Check `.vscodeignore` doesn't exclude `bin/` or `compiler/`
4. Verify uv is executable (Unix): `file bin/{platform}/uv`

### Package Size

Expected sizes:

- VSIX with single platform: ~22MB (mostly uv binary)
- uv binary: ~20MB
- Compiler source: ~200KB

If the VSIX is much smaller, bundling may have failed:

1. Run `make prepare` before packaging
2. Check that `bin/{platform}/uv` exists
3. Check that `compiler/src/` exists

### Download Fails

If `download_uv.sh` fails:

1. Check internet connection
2. Verify the uv version exists at <https://github.com/astral-sh/uv/releases>
3. Check for proxy/firewall issues

For more details on the architecture and development workflow, see [README.md](./README.md).
