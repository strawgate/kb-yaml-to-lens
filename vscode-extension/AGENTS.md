# Agent Guidelines: VS Code Extension

> TypeScript extension for live YAML dashboard compilation and preview

---

## Code Conventions

See root CODE_STYLE.md and CODERABBIT.md for detailed conventions.

---

## Quick Reference

### Essential Commands

Component-specific (from `vscode-extension/`):

| Command | Purpose |
| ------- | ------- |
| `make install` | Install dependencies |
| `make ci` | Run all CI checks |
| `make fix` | Auto-fix linting |
| `make compile` | Build TypeScript |
| `make watch` | Watch mode |
| `make test` | Run tests |
| `make package` | Create .vsix package |

Root-level (from repository root):

| Command | Purpose |
| ------- | ------- |
| `make install` | Install all components |
| `make ci` | Run all checks |
| `make fix` | Auto-fix all linting |

### Development Workflow

```bash
make install                    # First time (from root)
cd vscode-extension && make watch  # Watch mode, then F5 in VS Code
make ci && cd .. && make ci     # Run extension + all checks
```

---

## Architecture

### Overview

Hybrid TypeScript + Python:

- **TypeScript Extension** manages UI, commands, Python subprocess
- **Python Server** handles compilation using `dashboard_compiler`

### File Structure

| File | Purpose |
| ---- | ------- |
| `src/extension.ts` | Main entry, command registration |
| `src/compiler.ts` | Python subprocess management |
| `src/previewPanel.ts` | Webview preview panel |
| `src/gridEditorPanel.ts` | Visual grid editor |
| `src/fileWatcher.ts` | File change detection |
| `python/compile_server.py` | Stdio-based Python server |

### Key Components

**Compiler Service** (`compiler.ts`):

- Manages Python subprocess
- Sends compilation requests via stdin
- Receives JSON via stdout
- Handles errors and crashes

**Schema Registration** (`extension.ts`):

- Registers JSON schema with Red Hat YAML extension
- Fetches from LSP server (`dashboard/getSchema`)
- Provides auto-complete, validation, hover docs

**Preview Panel** (`previewPanel.ts`):

- Webview-based preview
- Auto-refreshes on save
- Export to NDJSON

**Grid Editor** (`gridEditorPanel.ts`):

- Drag-and-drop repositioning
- Interactive resizing
- Automatic YAML updates

---

## Extension Commands

Via Command Palette:

- `yamlDashboard.compile` - Compile current file
- `yamlDashboard.preview` - Open preview
- `yamlDashboard.editLayout` - Open grid editor
- `yamlDashboard.export` - Export to NDJSON

---

## Configuration

| Setting | Type | Description | Default |
| ------- | ---- | ----------- | ------- |
| `yamlDashboard.pythonPath` | string | Python interpreter path | `"python"` |
| `yamlDashboard.compileOnSave` | boolean | Auto-compile on save | `true` |

---

## Development Guidelines

### TypeScript Style

- Use strict mode
- Avoid `any` types
- Use async/await
- Handle errors explicitly

### Python Server Protocol

Stdio-based JSON-RPC:

**Request:**

```json
{
  "method": "compile",
  "params": { "file_path": "/path/to/dashboard.yaml" }
}
```

**Response (success):**

```json
{
  "success": true,
  "result": { "dashboard": {...}, "data_view": {...} }
}
```

**Response (error):**

```json
{
  "success": false,
  "error": "Error message"
}
```

### Webview Guidelines

- Use VS Code webview API
- Sanitize HTML
- Use message passing for communication
- Handle lifecycle (dispose, reveal)

---

## Testing

### Manual Testing

1. Press F5 in VS Code
2. Open test YAML (e.g., `inputs/esql-controls-example.yaml`)
3. Test commands

### Automated Testing

```bash
npm test
```

Tests in `src/test/`:

- `suite/` - Integration tests
- `unit/` - Unit tests

---

## Common Issues

**Python Server Not Starting**: Verify `dashboard_compiler` installed, check Python path

**Compilation Errors**: Check YAML syntax, verify schema

**Preview Not Updating**: Check `compileOnSave` enabled, manually run command

---

## AI Agent Guidelines

### Before Making Changes

1. Read relevant files first
2. Understand TypeScript ↔ Python boundary
3. Check existing command patterns
4. Test in Extension Development Host

### Verification

TypeScript compiles (`make compile`), ESLint passes, extension loads (F5), commands work, no console errors, Python server starts, `make ci` passes

### Working with Python Server

When modifying `python/compile_server.py`:

1. Maintain stdio JSON-RPC protocol
2. Test success and error paths
3. Ensure proper error handling
4. Remember: runs as subprocess

---

## Related Resources

| Resource | Location |
| -------- | -------- |
| Main repository | `../README.md` |
| Python compiler | `../src/dashboard_compiler/` |
| Extension README | `README.md` |
| VS Code API | <https://code.visualstudio.com/api> |
