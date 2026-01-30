# Developing: VS Code Extension

This guide covers development workflows for the VS Code extension.

## Prerequisites

- Node.js 20+
- npm
- VS Code (for testing)

## Setup

```bash
cd packages/vscode-extension
npm install
npm run compile
```

## Commands

Run from the repository root using the passthrough pattern:

| Command | Purpose |
| ------- | ------- |
| `make vscode install` | Install dependencies |
| `make vscode ci` | Run all CI checks |
| `make vscode fix` | Auto-fix linting |
| `make vscode compile` | Build TypeScript |
| `make vscode watch` | Watch mode for development |
| `make vscode test` | Run all tests |
| `make vscode package` | Create .vsix package |

For all commands, see `make vscode help`.

**From within component directory:** You can also run `make <target>` directly from `packages/vscode-extension/`.

## Development Workflow

1. Install dependencies: `make vscode install`
2. Start watch mode: `make vscode watch`
3. Press **F5** in VS Code to launch Extension Development Host
4. Make changes—TypeScript recompiles automatically
5. Reload Extension Development Host to see changes

## Architecture

**Hybrid TypeScript + Python:**

- **TypeScript Extension** manages UI, commands, Python subprocess
- **Python Server** handles compilation using `dashboard_compiler`

| File | Purpose |
| ---- | ------- |
| `src/extension.ts` | Main entry, command registration |
| `src/compiler.ts` | Python subprocess management |
| `src/previewPanel.ts` | Webview preview panel |
| `src/gridEditorPanel.ts` | Visual grid editor |
| `packages/kb-dashboard-cli/src/dashboard_compiler/lsp/server.py` | Stdio-based LSP server (in CLI component) |

### Extension Commands

| Command | Description |
| ------- | ----------- |
| `yamlDashboard.compile` | Compile current file |
| `yamlDashboard.preview` | Open preview panel |
| `yamlDashboard.editLayout` | Open visual grid editor |
| `yamlDashboard.export` | Export to NDJSON |

## Testing

### Test Philosophy

Focus on **high-value, maintainable tests** that validate business logic:

- **Python tests**: Core functionality (YAML parsing, grid updates, error handling)
- **E2E Extension tests**: Extension functionality in a real VS Code environment
- Avoid low-value smoke tests that only check if classes exist

### Running Tests

```bash
# All tests (from repository root)
make vscode test

# TypeScript unit tests only (from repository root)
make vscode test-unit

# E2E tests (from repository root)
make vscode test-e2e

# Or run directly from within vscode-extension directory
# cd packages/vscode-extension && npm test
```

### Python Tests

Python tests for LSP functionality are located in the compiler component:

- `packages/kb-dashboard-cli/tests/lsp/test_grid_updater.py` — Grid coordinate updates in YAML
- `packages/kb-dashboard-cli/tests/lsp/test_server.py` — LSP server functionality

```bash
# Run Python LSP tests (from repository root)
make cli test
# Or run specific LSP tests:
cd packages/kb-dashboard-cli && uv run pytest tests/lsp/ -v
```

### Test Coverage

Currently tested:

- Grid extraction from YAML files
- Grid coordinate updates
- YAML formatting preservation
- Error handling for missing files
- Input validation (panel IDs, grid coordinates)
- Path traversal prevention

## Building and Packaging

### Development Build (Current Platform)

```bash
make vscode prepare      # Download uv
make vscode package      # Create .vsix
```

### Release Build (All Platforms)

```bash
make vscode prepare-all  # Download uv for all platforms
make vscode package      # Create .vsix
```

### How It Works

The extension uses **uvx** to run `kb-dashboard-cli` directly from PyPI:

```bash
uv tool run kb-dashboard-cli==0.2.5 lsp
```

This means:

- No Python source code is bundled in the extension
- The package is fetched from PyPI on first run (then cached)
- Dependencies are resolved automatically by uv

### What Gets Bundled

| Component | Size | Notes |
| --------- | ---- | ----- |
| uv binary | ~20MB | Platform-specific |
| Compiled TypeScript | varies | out/ directory |

The Python package is fetched from PyPI at runtime via uvx.

### Platform Directories

| Platform | Directory | Binary |
| -------- | --------- | ------ |
| Linux x64 | `bin/linux-x64/` | `uv` |
| macOS Intel | `bin/darwin-x64/` | `uv` |
| macOS ARM64 | `bin/darwin-arm64/` | `uv` |
| Windows x64 | `bin/win32-x64/` | `uv.exe` |

## Troubleshooting

### Python Server Not Starting

1. Check Output panel: View → Output → "Dashboard Compiler LSP"
2. Verify internet connectivity (first run downloads from PyPI)
3. For development, verify `dashboard_compiler` is installed: `uv sync`

### Preview Not Updating

1. Check `compileOnSave` setting
2. Run compile command manually

### Extension Falls Back to Python

In production, if extension falls back to Python:

1. Verify uv exists: `ls bin/{platform}/uv`
2. Check `.vscodeignore` doesn't exclude `bin/`

### Package Too Small

Expected VSIX size: ~22MB. If much smaller:

1. Run `make vscode prepare` before packaging
2. Verify `bin/{platform}/uv` exists
