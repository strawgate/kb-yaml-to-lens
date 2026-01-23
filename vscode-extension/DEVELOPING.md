# Developing: VS Code Extension

This guide covers development workflows for the VS Code extension.

## Prerequisites

- Node.js 20+
- npm
- VS Code (for testing)

## Setup

```bash
cd vscode-extension
npm install
npm run compile
```

## Commands

Run from the `vscode-extension/` directory, or use pass-through from the repository root:

| Command | Purpose |
| ------- | ------- |
| `make install` | Install dependencies |
| `make ci` | Run all CI checks |
| `make fix` | Auto-fix linting |
| `make compile` | Build TypeScript |
| `make watch` | Watch mode for development |
| `make test` | Run all tests |
| `make package` | Create .vsix package |

For all commands, see `make help`.

**From repository root:** Use `make vscode <target>` (e.g., `make vscode test`).

## Development Workflow

1. Install dependencies: `make install`
2. Start watch mode: `make watch`
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
| `compiler/src/dashboard_compiler/lsp/server.py` | Stdio-based LSP server (in compiler component) |

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
# All tests
make test

# TypeScript unit tests only
make test-unit

# E2E tests (requires xvfb on Linux)
npm test
```

### Python Tests

Python tests for LSP functionality are located in the compiler component:

- `compiler/tests/lsp/test_grid_updater.py` — Grid coordinate updates in YAML
- `compiler/tests/lsp/test_server.py` — LSP server functionality

```bash
# Run Python LSP tests (from compiler directory)
cd compiler
uv run pytest tests/lsp/ -v
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
make prepare      # Download uv + bundle compiler
make package      # Create .vsix
```

### Release Build (All Platforms)

```bash
make prepare-all  # Download uv for all platforms + bundle compiler
make package      # Create .vsix
```

### What Gets Bundled

| Component | Size | Notes |
| --------- | ---- | ----- |
| uv binary | ~20MB | Platform-specific |
| Compiler source | ~200KB | pyproject.toml, uv.lock, src/ |
| Compiled TypeScript | varies | out/ directory |

Python virtualenv is created at first run by uv.

### Platform Directories

| Platform | Directory | Binary |
| -------- | --------- | ------ |
| Linux x64 | `bin/linux-x64/` | `uv` |
| macOS Intel | `bin/darwin-x64/` | `uv` |
| macOS ARM64 | `bin/darwin-arm64/` | `uv` |
| Windows x64 | `bin/win32-x64/` | `uv.exe` |

## Troubleshooting

### Python Server Not Starting

1. Verify `dashboard_compiler` is installed: `uv sync`
2. Check Python path in settings
3. Check Output panel: View → Output → "Kibana Dashboard Compiler"

### Preview Not Updating

1. Check `compileOnSave` setting
2. Run compile command manually

### Extension Falls Back to Python

In production, if extension falls back to Python:

1. Verify uv exists: `ls bin/{platform}/uv`
2. Verify compiler bundled: `ls compiler/pyproject.toml`
3. Check `.vscodeignore` doesn't exclude `bin/` or `compiler/`

### Package Too Small

Expected VSIX size: ~22MB. If much smaller:

1. Run `make prepare` before packaging
2. Verify `bin/{platform}/uv` exists
3. Verify `compiler/src/` exists
